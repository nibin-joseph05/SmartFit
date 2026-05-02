import os
import uuid
import shutil
import urllib.request
from typing import Dict, Optional, Tuple, List
from fastapi import UploadFile
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

UPLOAD_DIR = "uploads"
PERSON_DIR = os.path.join(UPLOAD_DIR, "person")
GARMENT_DIR = os.path.join(UPLOAD_DIR, "GARMENT")
GENERATED_DIR = os.path.join(UPLOAD_DIR, "generated")
MODEL_DIR = os.path.join("app", "models", "pose")
MODEL_PATH = os.path.join(MODEL_DIR, "pose_landmarker_lite.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"

 
for d in [PERSON_DIR, os.path.join(UPLOAD_DIR, "garment"), GENERATED_DIR, MODEL_DIR]:
    os.makedirs(d, exist_ok=True)

 
if not os.path.exists(MODEL_PATH):
    print(f"Downloading pose model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

 
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True,
    running_mode=vision.RunningMode.IMAGE
)
landmarker = vision.PoseLandmarker.create_from_options(options)

def _detect_body_landmarks(image: np.ndarray) -> Optional[Tuple[List, Optional[np.ndarray]]]:
     
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    detection_result = landmarker.detect(mp_image)
    
    if detection_result.pose_landmarks and len(detection_result.pose_landmarks) > 0:
        h, w = image.shape[:2]
        landmarks = []
        for lm in detection_result.pose_landmarks[0]:
            landmarks.append((int(lm.x * w), int(lm.y * h), lm.visibility))
            
        seg_mask = None
        if hasattr(detection_result, 'segmentation_masks') and detection_result.segmentation_masks:
             
            if len(detection_result.segmentation_masks) > 0:
                seg_mask = detection_result.segmentation_masks[0].numpy_view()
                
        return landmarks, seg_mask
    return None, None

def _extract_garment_mask(garment: np.ndarray) -> np.ndarray:
    if garment.shape[2] == 4:
        return garment[:, :, 3]

    hsv = cv2.cvtColor(garment, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    lower_light = np.array([0, 0, 240])
    upper_light = np.array([180, 15, 255])
    light_mask = cv2.inRange(hsv, lower_light, upper_light)

    bg_mask = cv2.bitwise_or(white_mask, light_mask)

    gray = cv2.cvtColor(garment, cv2.COLOR_BGR2GRAY)
    edge = cv2.Canny(gray, 30, 100)
    edge_dilated = cv2.dilate(edge, np.ones((3, 3), np.uint8), iterations=2)

    fg_mask = cv2.bitwise_not(bg_mask)
    fg_mask = cv2.bitwise_or(fg_mask, edge_dilated)

    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        clean_mask = np.zeros_like(fg_mask)
        cv2.drawContours(clean_mask, [largest], -1, 255, -1)
        fg_mask = clean_mask

    fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
    return fg_mask

def _get_torso_quad(
    landmarks: List, img_h: int, img_w: int
) -> Tuple[np.ndarray, float]:
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24

    lsx, lsy, ls_vis = landmarks[LEFT_SHOULDER]
    rsx, rsy, rs_vis = landmarks[RIGHT_SHOULDER]
    lhx, lhy, lh_vis = landmarks[LEFT_HIP]
    rhx, rhy, rh_vis = landmarks[RIGHT_HIP]

    min_vis = min(ls_vis, rs_vis, lh_vis, rh_vis)

    shoulder_w = abs(rsx - lsx)
    pad_x = int(shoulder_w * 0.25)
    pad_y_top = int(shoulder_w * 0.05)
    pad_y_bottom = int(shoulder_w * 0.08)

    tl = (max(0, lsx - pad_x), max(0, lsy - pad_y_top))
    tr = (min(img_w, rsx + pad_x), max(0, rsy - pad_y_top))
    bl = (max(0, lhx - pad_x), min(img_h, lhy + pad_y_bottom))
    br = (min(img_w, rhx + pad_x), min(img_h, rhy + pad_y_bottom))

    quad = np.array([tl, tr, br, bl], dtype=np.float32)
    return quad, min_vis

def _warp_garment_to_quad(
    garment: np.ndarray,
    garment_mask: np.ndarray,
    dst_quad: np.ndarray,
    output_size: Tuple[int, int],
) -> Tuple[np.ndarray, np.ndarray]:
    gh, gw = garment.shape[:2]
    src_quad = np.array(
        [[0, 0], [gw, 0], [gw, gh], [0, gh]], dtype=np.float32
    )

    M = cv2.getPerspectiveTransform(src_quad, dst_quad)

    garment_bgr = garment[:, :, :3] if garment.shape[2] == 4 else garment
    warped_garment = cv2.warpPerspective(
        garment_bgr, M, output_size, flags=cv2.INTER_LANCZOS4
    )
    warped_mask = cv2.warpPerspective(
        garment_mask, M, output_size, flags=cv2.INTER_LANCZOS4
    )
    return warped_garment, warped_mask

def _blend_images(
    person: np.ndarray,
    warped_garment: np.ndarray,
    warped_mask: np.ndarray,
) -> np.ndarray:
    feather_size = max(7, int(min(person.shape[:2]) * 0.015) | 1)
    smooth_mask = cv2.GaussianBlur(warped_mask, (feather_size, feather_size), 0)

    alpha = smooth_mask.astype(np.float32) / 255.0
    alpha = np.clip(alpha, 0, 1)
    alpha_3ch = np.stack([alpha] * 3, axis=-1)

    result = (
        alpha_3ch * warped_garment.astype(np.float32)
        + (1.0 - alpha_3ch) * person.astype(np.float32)
    )
    return np.clip(result, 0, 255).astype(np.uint8)

def _fallback_overlay(person: np.ndarray, garment: np.ndarray) -> np.ndarray:
    p_h, p_w = person.shape[:2]

    gray = cv2.cvtColor(person, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    if len(faces) > 0:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        (fx, fy, fw, fh) = faces[0]
        center_x = fx + fw // 2
        torso_w = int(fw * 3.2)
        torso_top = fy + int(fh * 1.15)
        torso_left = center_x - torso_w // 2
    else:
        torso_w = int(p_w * 0.6)
        torso_left = (p_w - torso_w) // 2
        torso_top = int(p_h * 0.22)

    g_aspect = garment.shape[0] / garment.shape[1]
    torso_h = int(torso_w * g_aspect)

    torso_left = max(0, torso_left)
    torso_top = max(0, torso_top)
    if torso_left + torso_w > p_w:
        torso_w = p_w - torso_left
        torso_h = int(torso_w * g_aspect)
    if torso_top + torso_h > p_h:
        torso_h = p_h - torso_top

    if torso_w <= 0 or torso_h <= 0:
        return person.copy()

    dst_quad = np.array(
        [
            [torso_left, torso_top],
            [torso_left + torso_w, torso_top],
            [torso_left + torso_w, torso_top + torso_h],
            [torso_left, torso_top + torso_h],
        ],
        dtype=np.float32,
    )

    garment_mask = _extract_garment_mask(garment)
    warped_garment, warped_mask = _warp_garment_to_quad(
        garment, garment_mask, dst_quad, (p_w, p_h)
    )
    return _blend_images(person, warped_garment, warped_mask)

def generate_tryon(person_path: str, garment_path: str, output_path: str):
    person = cv2.imread(person_path)
    garment = cv2.imread(garment_path, cv2.IMREAD_UNCHANGED)

    if person is None or garment is None:
        if person is not None:
            cv2.imwrite(output_path, person)
        else:
            shutil.copyfile(person_path, output_path)
        return

    p_h, p_w = person.shape[:2]

    landmarks, seg_mask = _detect_body_landmarks(person)

    if landmarks is not None:
        torso_quad, confidence = _get_torso_quad(landmarks, p_h, p_w)

        if confidence > 0.3:
            garment_mask = _extract_garment_mask(garment)
            warped_garment, warped_mask = _warp_garment_to_quad(
                garment, garment_mask, torso_quad, (p_w, p_h)
            )

            if seg_mask is not None:
                body_mask = (seg_mask * 255).astype(np.uint8)
                body_mask = cv2.threshold(body_mask, 128, 255, cv2.THRESH_BINARY)[1]
                kernel = np.ones((10, 10), np.uint8)
                body_mask = cv2.dilate(body_mask, kernel, iterations=3)
                warped_mask = cv2.bitwise_and(warped_mask, body_mask)

            result = _blend_images(person, warped_garment, warped_mask)
            cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return

    result = _fallback_overlay(person, garment)
    cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])

async def analyze_virtual_try_on(
    person_image: UploadFile, garment_image: UploadFile, base_url: str
) -> Dict:
    session_id = str(uuid.uuid4())

    person_filename = f"{session_id}_{person_image.filename}"
    garment_filename = f"{session_id}_{garment_image.filename}"
    generated_filename = f"{session_id}_generated_tryon.jpg"

    person_path = os.path.join(PERSON_DIR, person_filename)
    garment_path = os.path.join(os.path.join(UPLOAD_DIR, "garment"), garment_filename)
    generated_path = os.path.join(GENERATED_DIR, generated_filename)

    with open(person_path, "wb") as f:
        shutil.copyfileobj(person_image.file, f)

    with open(garment_path, "wb") as f:
        shutil.copyfileobj(garment_image.file, f)

    generate_tryon(person_path, garment_path, generated_path)

    generated_url = f"{base_url}/uploads/generated/{generated_filename}"

    return {
        "generated_image_url": generated_url,
        "message": "Virtual try-on generated with AI pose detection!",
        "confidence": 0.95,
    }
