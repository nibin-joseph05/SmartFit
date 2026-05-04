import cv2
import numpy as np

def extract_garment_mask(garment: np.ndarray) -> np.ndarray:
    if garment.shape[2] == 4:
        alpha = garment[:, :, 3]
        if cv2.countNonZero(alpha) > alpha.size * 0.1:
            return alpha

    hsv = cv2.cvtColor(garment, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0,   0, 190])
    upper_white = np.array([180, 40, 255])
    white_mask  = cv2.inRange(hsv, lower_white, upper_white)

    lower_grey = np.array([0,  0, 220])
    upper_grey = np.array([180, 20, 255])
    grey_mask  = cv2.inRange(hsv, lower_grey, upper_grey)

    bg_mask = cv2.bitwise_or(white_mask, grey_mask)

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
        if cv2.contourArea(largest) > 500:
            clean_mask = np.zeros_like(fg_mask)
            cv2.drawContours(clean_mask, [largest], -1, 255, -1)
            fg_mask = clean_mask

    if cv2.countNonZero(fg_mask) < fg_mask.size * 0.05:
        fg_mask[:] = 255

    fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
    return fg_mask

def warp_garment_to_quad(
    garment: np.ndarray,
    garment_mask: np.ndarray,
    dst_quad: np.ndarray,
    output_size: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
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

def blend_images(
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

def fallback_overlay(person: np.ndarray, garment: np.ndarray) -> np.ndarray:
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

    garment_mask = extract_garment_mask(garment)
    warped_garment, warped_mask = warp_garment_to_quad(
        garment, garment_mask, dst_quad, (p_w, p_h)
    )
    return blend_images(person, warped_garment, warped_mask)
