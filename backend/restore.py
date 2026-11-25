
import cv2
import torch
import numpy as np
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "RealESRGAN_x4plus.pth"

# CPU processing
device = torch.device("cpu")

# Real-ESRGAN model
model = RRDBNet(
    num_in_ch=3,
    num_out_ch=3,
    num_feat=64,
    num_block=23,
    num_grow_ch=32,
    scale=4
)

upsampler = RealESRGANer(
    scale=4,
    model_path=str(MODEL_PATH),
    model=model,
    tile=128,
    tile_pad=10,
    pre_pad=0,
    half=False,
    device=device
)


def clean_document(image):

    # Estimate the paper background
    height, width = image.shape[:2]

    sigma = max(15, min(height, width) / 25)

    background = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma
    )

    # Prevent division by zero
    background = np.maximum(background, 1)

    # Correct yellow colour cast
    image_float = image.astype(np.float32)
    background_float = background.astype(np.float32)

    target_white = 245.0

    gain = target_white / background_float
    gain = np.clip(gain, 0.8, 1.8)

    corrected = image_float * gain

    corrected = np.clip(
        corrected, 0, 255
    ).astype(np.uint8)

    return corrected


def restore_image(input_path, output_path):

    # Read original image
    image = cv2.imread(str(input_path))

    if image is None:
        raise ValueError("Could not read the uploaded image")

    # AI resolution enhancement
    restored, _ = upsampler.enhance(
        image,
        outscale=4
    )

    # Reduce yellow paper background
    final_image = clean_document(restored)

    # Save restored image
    success = cv2.imwrite(
        str(output_path),
        final_image
    )

    if not success:
        raise ValueError("Could not save restored image")

    return str(output_path)
