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

def get_torso_quad(
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
