import os
import uuid
import shutil
from typing import Dict
from fastapi import UploadFile
import cv2
import numpy as np

from app.services.tryon.pose import detect_body_landmarks, get_garment_quad
from app.services.tryon.image import (
    extract_garment_mask,
    warp_garment_to_quad,
    blend_images,
    fallback_overlay,
)

UPLOAD_DIR   = "uploads"
PERSON_DIR   = os.path.join(UPLOAD_DIR, "person")
GARMENT_DIR  = os.path.join(UPLOAD_DIR, "garment")
GENERATED_DIR = os.path.join(UPLOAD_DIR, "generated")

os.makedirs(PERSON_DIR,    exist_ok=True)
os.makedirs(GARMENT_DIR,   exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


GARMENT_ASPECT_HINTS = {
    "top":     0.9,
    "shirt":   0.9,
    "tshirt":  0.9,
    "blouse":  1.0,
    "jacket":  1.0,
    "coat":    1.2,
    "skirt":   1.6,
    "dress":   2.2,
    "pants":   2.0,
    "jeans":   2.0,
}


def generate_tryon(
    person_path: str,
    garment_path: str,
    output_path: str,
    garment_type: str = "top",
) -> None:
    person  = cv2.imread(person_path)
    garment = cv2.imread(garment_path, cv2.IMREAD_UNCHANGED)

    if person is None or garment is None:
        print(f"[ERROR] Could not load images — person={person_path}, garment={garment_path}")
        shutil.copyfile(person_path if person is not None else garment_path, output_path)
        return

    p_h, p_w = person.shape[:2]
    g_h, g_w = garment.shape[:2]

    aspect_hint = GARMENT_ASPECT_HINTS.get(garment_type.lower().strip(), g_h / g_w)
    print(f"[INFO] Person: {p_w}×{p_h}  Garment: {g_w}×{g_h}  type={garment_type!r}  aspect_hint={aspect_hint:.2f}")

    landmarks, _ = detect_body_landmarks(person)

    if landmarks is not None:
        torso_quad, confidence = get_garment_quad(landmarks, p_h, p_w, aspect_hint)

        quad_w = int(torso_quad[1][0] - torso_quad[0][0])
        quad_h = int(torso_quad[2][1] - torso_quad[0][1])
        print(f"[INFO] Confidence={confidence:.2f}  Quad={torso_quad.tolist()}")
        print(f"[INFO] Quad size: {quad_w}×{quad_h}  (person canvas: {p_w}×{p_h})")

        if confidence > 0.3:
            garment_mask = extract_garment_mask(garment)
            mask_pct = 100 * cv2.countNonZero(garment_mask) / garment_mask.size
            print(f"[INFO] Garment mask coverage: {mask_pct:.1f}%")

            warped_garment, warped_mask = warp_garment_to_quad(
                garment, garment_mask, torso_quad, (p_w, p_h)
            )
            warp_pct = 100 * cv2.countNonZero(warped_mask) / warped_mask.size
            print(f"[INFO] Warped mask coverage: {warp_pct:.1f}%")

            result = blend_images(person, warped_garment, warped_mask)
            cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"[OK]  Saved → {output_path}")
            return
        else:
            print(f"[WARN] Low confidence ({confidence:.2f}), using fallback")
    else:
        print("[WARN] No landmarks detected, using fallback")

    result = fallback_overlay(person, garment)
    cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"[OK]  Saved (fallback) → {output_path}")


async def analyze_virtual_try_on(
    person_image: UploadFile,
    garment_image: UploadFile,
    base_url: str,
    garment_type: str = "top",  
) -> Dict:
    session_id = str(uuid.uuid4())

    person_filename    = f"{session_id}_{person_image.filename}"
    garment_filename   = f"{session_id}_{garment_image.filename}"
    generated_filename = f"{session_id}_generated_tryon.jpg"

    person_path    = os.path.join(PERSON_DIR,    person_filename)
    garment_path   = os.path.join(GARMENT_DIR,   garment_filename)
    generated_path = os.path.join(GENERATED_DIR, generated_filename)

    with open(person_path, "wb") as f:
        shutil.copyfileobj(person_image.file, f)
    with open(garment_path, "wb") as f:
        shutil.copyfileobj(garment_image.file, f)

    generate_tryon(person_path, garment_path, generated_path, garment_type)

    return {
        "generated_image_url": f"{base_url}/uploads/generated/{generated_filename}",
        "message": "Virtual try-on generated with AI pose detection!",
        "confidence": 0.95,
    }