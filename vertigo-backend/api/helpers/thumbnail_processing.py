import requests
import shutil
import re
import os
import uuid
from PIL import Image
from flask import current_app
from slugify import slugify

import requests
import shutil
import re
import uuid
from PIL import Image

def save_series_thumbnail(url, title):
    if url != "noimage":
        request = requests.get(url, stream=True)
        ext = re.search('\.(\w+)(?!.*\.)', url).group(1)

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
                print(url)  # here you get the file causing the exception
                print(e)

        filename = f"{uuid.uuid4()}{slugify(title)}{extension}"

        if request.status_code == 200:
            request.raw.decode_content = True
            with open(current_app.config['cover_path']+"/"+filename, 'wb') as f:
                shutil.copyfileobj(request.raw, f)

            print('Image successfully Downloaded: ', filename)

            # Logic for determining dominant color and saving it to the database
            dominant_color = calculate_dominant_color(filename)
            return filename, dominant_color

    else:
        print('Image Couldn\'t be retrieved')
        return None, None

def calculate_dominant_color(filename):
    def increase_brightness(color):
        for i in range(len(color)):
            if 100 < color[i] < 150:
                color[i] += 50
        return color

    def get_dominant_color(pil_img, palette_size=16):
        img = pil_img.copy()
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

    im = Image.open(current_app.config['cover_path']+"/"+filename)
    dominant_color = get_dominant_color(im)
    return f"({dominant_color[0]},{dominant_color[1]},{dominant_color[2]})"

def delete_series_thumbnail(filename):
    file_path = os.path.join(current_app.config['cover_path'], filename)
    os.remove(file_path)
