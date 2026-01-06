import os
import random
from PIL import Image, ImageOps
from flask import current_app
from api.background import executor

TILE_W = 216
TILE_H = 320

GRID_COLS = 8
GRID_ROWS = 5

OUTPUT_FORMAT = "WEBP"
OUTPUT_QUALITY = 82
BACKGROUND_FILE = "cover_collage.webp"
BACKGROUND_PATH = os.path.join("./Config",BACKGROUND_FILE)

def generate_background_image(
    image_paths: list[str],
    output_path: str,
):
    """
    Generates a tiled comic-cover background image.
    """

    if not image_paths:
        raise ValueError("No image paths provided")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    needed = GRID_COLS * GRID_ROWS

    # Repeat images if insufficient
    while len(image_paths) < needed:
        image_paths += image_paths

    random.shuffle(image_paths)
    image_paths = image_paths[:needed]

    background_width = GRID_COLS * TILE_W
    background_height = GRID_ROWS * TILE_H

    background = Image.new("RGB", (background_width, background_height), (15, 15, 20))

    idx = 0
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            img_path = image_paths[idx]
            idx += 1

            try:
                img = Image.open(img_path).convert("RGB")
            except Exception:
                continue

            img = ImageOps.fit(
                img,
                (TILE_W, TILE_H),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )

            x = col * TILE_W
            y = row * TILE_H

            background.paste(img, (x, y))

    background.save(
        output_path,
        OUTPUT_FORMAT,
        quality=OUTPUT_QUALITY,
        method=6,
    )

def regenerate_background(input_folder: str):
    """Generate background from all images in the input folder."""
    image_paths = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    if not image_paths:
        return

    output_path = BACKGROUND_PATH
    generate_background_image(image_paths, output_path)

def submit_background_regeneration(input_folder: str):
    executor.submit(regenerate_background, input_folder)