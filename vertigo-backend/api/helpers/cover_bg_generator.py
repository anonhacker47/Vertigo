"""
Tiled cover collage used as the login page background.

The login page is served before authentication, so there is a single collage at
``<DATA_DIR>/cover_collage.webp``. It is rebuilt from the series covers of whichever
user last changed a cover.
"""
import glob
import os
import random
from PIL import Image, ImageOps

from api import media

TILE_W = 216
TILE_H = 320

GRID_COLS = 8
GRID_ROWS = 5

OUTPUT_FORMAT = "WEBP"
OUTPUT_QUALITY = 82
BACKGROUND_FILE = "cover_collage.webp"

_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def background_path() -> str:
    return os.path.join(media.data_dir(), BACKGROUND_FILE)


def generate_background_image(image_paths: list[str], output_path: str) -> None:
    """Generates a tiled comic-cover background image."""
    if not image_paths:
        raise ValueError("No image paths provided")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    needed = GRID_COLS * GRID_ROWS
    image_paths = list(image_paths)
    while len(image_paths) < needed:
        image_paths += image_paths

    random.shuffle(image_paths)
    image_paths = image_paths[:needed]

    background = Image.new("RGB", (GRID_COLS * TILE_W, GRID_ROWS * TILE_H), (15, 15, 20))

    idx = 0
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            img_path = image_paths[idx]
            idx += 1
            try:
                img = Image.open(img_path).convert("RGB")
            except Exception:
                continue
            img = ImageOps.fit(img, (TILE_W, TILE_H), method=Image.Resampling.LANCZOS,
                               centering=(0.5, 0.5))
            background.paste(img, (col * TILE_W, row * TILE_H))

    background.save(output_path, OUTPUT_FORMAT, quality=OUTPUT_QUALITY, method=6)


def user_cover_paths(user_id) -> list[str]:
    """All series cover files for a user."""
    root = media.user_root(user_id)
    return [
        p for p in glob.glob(os.path.join(root, media.SERIES_DIR, "*", "cover.*"))
        if p.lower().endswith(_IMAGE_EXTS)
    ]


def regenerate_background(user_id) -> None:
    """Rebuild the collage from a user's series covers (no-op when they have none)."""
    paths = user_cover_paths(user_id)
    if not paths:
        return
    generate_background_image(paths, background_path())


def submit_background_regeneration(user_id) -> None:
    media.submit(regenerate_background, user_id)
