def analyze_fit(height: float, weight: float, dress_type: str, image_bytes: bytes) -> dict:
    """
    Simulates core processing of image and user details to return sizing.
    In a real MVP, this would route to AI models for processing.
    """
    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        size = "S"
    elif bmi < 24.9:
        size = "M"
    elif bmi < 29.9:
        size = "L"
    else:
        size = "XL"
        
    fit_classification = "Regular Fit" if dress_type.lower() in ['tshirt', 'shirt'] else "Relaxed Fit"
    confidence_level = 0.85
    
    return {
        "recommended_size": size,
        "fit_classification": fit_classification,
        "confidence": confidence_level
    }
