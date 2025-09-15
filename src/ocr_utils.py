import easyocr
import numpy as np
from PIL import Image

# Initialize EasyOCR reader (English + Hindi + Marathi)
reader = easyocr.Reader(['en', 'hi', 'mr'])

def extract_text(image_file):
    """
    Extract text from an uploaded image using EasyOCR.
    Returns list of lines with confidence scores.
    """
    # Open image
    image = Image.open(image_file)
    image = np.array(image)

    # Run OCR
    results = reader.readtext(image)

    # Collect text + confidence
    extracted_text = []
    for (bbox, text, prob) in results:
        extracted_text.append({
            "text": text,
            "confidence": round(prob * 100, 2)
        })

    return extracted_text
