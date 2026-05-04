import os
import urllib.request
from typing import Optional, Tuple, List
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_DIR = os.path.join("app", "models", "pose")
MODEL_PATH = os.path.join(MODEL_DIR, "pose_landmarker_lite.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"

os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    print(f"Downloading pose model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,
    running_mode=vision.RunningMode.IMAGE
)
landmarker = vision.PoseLandmarker.create_from_options(options)

def detect_body_landmarks(image: np.ndarray) -> Optional[Tuple[List, Optional[np.ndarray]]]:
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

def get_garment_quad(
    landmarks: List, img_h: int, img_w: int, garment_aspect_ratio: float
) -> Tuple[np.ndarray, float]:
    """
    garment_aspect_ratio = height / width
    > 1.5  → full-length dress (quad reaches ankles)
    <= 1.5 → top/shirt (quad reaches hips)
    """
    LEFT_SHOULDER  = 11   
    RIGHT_SHOULDER = 12   
    LEFT_HIP       = 23
    RIGHT_HIP      = 24
    LEFT_ANKLE     = 27
    RIGHT_ANKLE    = 28

    lsx, lsy, ls_vis = landmarks[LEFT_SHOULDER]
    rsx, rsy, rs_vis = landmarks[RIGHT_SHOULDER]
    lhx, lhy, lh_vis = landmarks[LEFT_HIP]
    rhx, rhy, rh_vis = landmarks[RIGHT_HIP]
    lax, lay, la_vis = landmarks[LEFT_ANKLE]
    rax, ray, ra_vis = landmarks[RIGHT_ANKLE]

    confidence = min(ls_vis, rs_vis)
    shoulder_w = abs(lsx - rsx)

    img_left_x  = min(lsx, rsx)   
    img_right_x = max(lsx, rsx)   
    shoulder_y  = int((lsy + rsy) / 2)

    pad_x     = int(shoulder_w * 0.28)
    pad_y_top = int(shoulder_w * 0.08)

    top_y = max(0, shoulder_y - pad_y_top)

    if garment_aspect_ratio > 1.5:
        if la_vis > 0.3 and ra_vis > 0.3:
            bottom_y = int(max(lay, ray)) + int(shoulder_w * 0.15)
        elif lh_vis > 0.3 and rh_vis > 0.3:
            hip_y    = int((lhy + rhy) / 2)
            torso_h  = hip_y - shoulder_y
            bottom_y = int(hip_y + torso_h * 2.0)
        else:
            bottom_y = int(img_h * 0.92)

        bottom_y = min(bottom_y, img_h - 5)

        pad_x = int(shoulder_w * 0.45)
    else:
        if lh_vis < 0.3 or rh_vis < 0.3:
            bottom_y = shoulder_y + int(shoulder_w * 2.2)
        else:
            bottom_y = int((lhy + rhy) / 2) + int(shoulder_w * 0.1)
        bottom_y = min(bottom_y, img_h - 5)

    tl = (max(0,     img_left_x  - pad_x), top_y)
    tr = (min(img_w, img_right_x + pad_x), top_y)
    br = (min(img_w, img_right_x + pad_x), bottom_y)
    bl = (max(0,     img_left_x  - pad_x), bottom_y)

    quad = np.array([tl, tr, br, bl], dtype=np.float32)
    return quad, confidence

def get_torso_quad(landmarks, img_h, img_w):
    return get_garment_quad(landmarks, img_h, img_w, garment_aspect_ratio=1.0)