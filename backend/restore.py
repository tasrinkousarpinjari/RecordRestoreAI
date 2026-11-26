
import cv2
import numpy as np
from pathlib import Path

def clean_document(image):
    # Correct uneven lighting and paper background
    image_float = image.astype(np.float32)

    height, width = image.shape[:2]
    sigma = max(15, min(height, width) / 25)

    background = cv2.GaussianBlur(
        image_float,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma
    )

    background = np.maximum(background, 1)

    # Normalize paper background
    corrected = image_float * (245.0 / background)
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)

    # Improve text and document contrast
    lab = cv2.cvtColor(corrected, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(l_channel)

    result = cv2.merge((enhanced, a_channel, b_channel))
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

    # Mild noise reduction
    result = cv2.fastNlMeansDenoisingColored(
        result, None, 3, 3, 7, 21
    )

    return result


def restore_image(input_path, output_path):
    # Read uploaded image
    image = cv2.imread(str(input_path))

    if image is None:
        raise ValueError("Could not read the uploaded image")

    # Resize only if image is extremely large
    height, width = image.shape[:2]
    max_dimension = 2000

    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    # Restore document quality
    final_image = clean_document(image)

    # Save output
    success = cv2.imwrite(str(output_path), final_image)

    if not success:
        raise ValueError("Could not save restored image")

    return str(output_path)
