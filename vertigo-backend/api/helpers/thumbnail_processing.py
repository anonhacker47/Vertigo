from urllib.parse import urlparse
import requests
import shutil
import re
import os
import uuid
from PIL import Image
from flask import current_app
from slugify import slugify
from api.utils.files import get_user_path
import requests
import shutil
import re
import uuid
from PIL import Image

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
}

THUMB_CACHE = {}

def handle_series_thumbnail(series, thumbnail, files, title, user_id, folder):
    thumbnail_filename = None
    dominant_color = None

    if thumbnail and thumbnail.startswith("http"):
        thumbnail_filename, dominant_color = download_thumbnail(
            thumbnail, title, user_id, folder
        )

    elif files and "thumbnail" in files:
        file = files["thumbnail"]
        thumbnail_filename, dominant_color = save_thumbnail(
            file, title, user_id, folder
        )

    if thumbnail_filename:
        series.thumbnail = thumbnail_filename
        series.dominant_color = dominant_color

def get_or_download_thumbnail(url: str, title: str, user_id: int, folder: str):
    """Return cached (path, dominant_color) for thumbnail, downloading if needed."""
    if not url:
        return None, None

    if url in THUMB_CACHE:
        return THUMB_CACHE[url]

    result = download_thumbnail(url, title, user_id, folder)

    # Normalize: result may be just path or (path, color)
    if isinstance(result, tuple):
        path, dominant_color = result
    else:
        path, dominant_color = result, None

    THUMB_CACHE[url] = (path, dominant_color)
    return path, dominant_color

def download_thumbnail(url, title, user_id, folder):
    if url != "noimage":

        request = requests.get(url, stream=True,headers=headers)
        ext = re.search(r'\.(\w+)(?!.*\.)', url).group(1)

        if "webp" in ext:
            extension = ".webp"
        elif "png" in ext:
            extension = ".png"
        elif "jpeg" or "jpg" in ext:
            extension = ".jpeg"
        else:
            print("no extensions")
            try:
                img = Image.open(request.raw)
                extension = f".{img.format}"
            except Exception as e:
                # print(url)  # here you get the file causing the exception
                print(e)

        filename = f"{uuid.uuid4()}{slugify(title)}{extension}"
        if request.status_code == 200:
            request.raw.decode_content = True
            save_dir = get_user_path(user_id, folder)
            save_path = os.path.join(save_dir, filename)
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(request.raw, f)

            print('Image successfully Downloaded: ', filename)
            if "Covers" in folder:
            # Logic for determining dominant color and saving it to the database
                dominant_color = calculate_dominant_color(filename,save_dir)
                return filename, dominant_color
            else:
                return filename
        else:
            print('Image Retrieval Failed')
    else:
        print('Image Couldn\'t be retrieved')
        return None, None

def save_thumbnail(file, title, user_id, folder):
    if not isinstance(file, str):
        ext = re.search(r'\.(\w+)(?!.*\.)', file.filename).group(1)

        if "webp" in ext:
            extension = ".webp"
        elif "png" in ext:
            extension = ".png"
        elif "jpeg" in ext or "jpg" in ext:
            extension = ".jpeg"
        else:
            print("no extensions")
            try:
                img = Image.open(file.raw)
                extension = f".{img.format}"
            except Exception as e:
                print(e)

        filename = f"{uuid.uuid4()}{slugify(title)}{extension}"

        if file:
            save_dir = get_user_path(user_id, folder)
            save_path = os.path.join(save_dir, filename)

            file.save(save_path)

            print('Image successfully Downloaded: ', filename)

            # Logic for determining dominant color and saving it to the database
            if "Covers" in folder:
            # Logic for determining dominant color and saving it to the database
                dominant_color = calculate_dominant_color(filename,save_dir)
                return filename, dominant_color
            else:
                return filename
    else:
        print('Image Couldn\'t be retrieved')
        return None, None

def calculate_dominant_color(filename,folder_path):
    def increase_brightness(color):
        for i in range(len(color)):
            if 100 < color[i] < 150:
                color[i] += 50
        return color

    def get_dominant_color(pil_img, palette_size=16):
        img = pil_img.copy()
        img = img.convert("RGB")
        img.thumbnail((100, 100))
        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        palette_index = color_counts[0][1]
        dominant_color = palette[palette_index*3:palette_index*3+3]
        i = 0
        while i < len(color_counts):
            palette = paletted.getpalette()
            color_counts = sorted(paletted.getcolors(), reverse=True)
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index*3:palette_index*3+3]
            if dominant_color[0] > 100 or dominant_color[1] > 100 or dominant_color[2] > 100:
                dominant_color = increase_brightness(dominant_color)
                return dominant_color
            else:
                i += 1
        return dominant_color
    
    path = os.path.join(folder_path, filename)
    im = Image.open(path)
    dominant_color = get_dominant_color(im)
    return f"({dominant_color[0]},{dominant_color[1]},{dominant_color[2]})"

def delete_thumbnail(filename, user_id, folder):
    base = get_user_path(user_id, folder)
    file_path = os.path.join(base, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

def delete_user_images(user_id):
    """
    Deletes all files inside:
        Covers/
        Entities/Publisher/
        Entities/Creator/
        Entities/Character/
    Does NOT delete 'Avatar/'
    Does NOT delete folder structure
    """

    base = os.path.join(current_app.config["user_path"], str(user_id))

    delete_folders = [
        "Covers",
        "Entities/Publisher",
        "Entities/Creator",
        "Entities/Character",
    ]

    for folder in delete_folders:
        folder_path = os.path.join(base, folder)

        if not os.path.exists(folder_path):
            continue

        # Remove all files inside the folder
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except Exception as e:
                    print(f"Error deleting file {f}: {e}")

def normalize_thumbnail(value):
    if not value:
        return None

    parsed = urlparse(value)

    path = parsed.path

    if path.startswith("/api/publisher/image/"):
        return path.replace("/api/publisher/image/", "", 1)

    return value