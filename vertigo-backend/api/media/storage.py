import io
import os
import shutil

import requests
from PIL import Image
from werkzeug.datastructures import FileStorage

from api.media.dominant_color import dominant_color
from api.media.paths import (
    AVATAR_DIR, SERIES_DIR, ENTITIES_DIR,
    user_root, safe_join, resolve, init_user_dirs,
)

MAX_IMAGE_BYTES = 20 * 1024 * 1024
_FORMAT_EXT = {"JPEG": ".jpeg", "PNG": ".png", "WEBP": ".webp", "GIF": ".gif"}
_DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
}


class MediaError(Exception):
    """A user-facing problem with an image source (bad URL, not an image, too large)."""


def _read_source(source) -> bytes:
    if isinstance(source, FileStorage):
        data = source.read(MAX_IMAGE_BYTES + 1)
    elif isinstance(source, str) and source.startswith(("http://", "https://")):
        try:
            resp = requests.get(source, headers=_DOWNLOAD_HEADERS, stream=True, timeout=20)
        except requests.RequestException as exc:
            raise MediaError(f"download failed: {exc}") from exc
        if resp.status_code != 200:
            raise MediaError(f"download failed (HTTP {resp.status_code})")
        buf = bytearray()
        for chunk in resp.iter_content(64 * 1024):
            buf.extend(chunk)
            if len(buf) > MAX_IMAGE_BYTES:
                raise MediaError("image too large")
        data = bytes(buf)
    else:
        raise MediaError("unsupported image source")

    if not data:
        raise MediaError("empty image")
    if len(data) > MAX_IMAGE_BYTES:
        raise MediaError("image too large")
    return data


def _sniff_ext(data: bytes) -> str:
    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = img.format
    except Exception as exc:
        raise MediaError("not a valid image") from exc
    ext = _FORMAT_EXT.get(fmt or "")
    if not ext:
        raise MediaError(f"unsupported image format {fmt}")
    return ext


def store(user_id, rel_dir: str, filename: str, source, *, replace=None,
          want_color: bool = False):

    data = _read_source(source)
    ext = _sniff_ext(data)
    filename = f"{filename}{ext}"
    relpath = f"{rel_dir}/{filename}"

    abs_dir = safe_join(user_root(user_id), rel_dir)
    if abs_dir is None:
        raise MediaError("invalid storage path")
    os.makedirs(abs_dir, exist_ok=True)

    full = os.path.join(abs_dir, filename)
    tmp = full + ".part"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, full)

    if replace and replace != relpath:
        remove(user_id, replace)

    color = dominant_color(full) if want_color else None
    return relpath, color


def remove(user_id, relpath) -> None:
    path = resolve(user_id, relpath)
    if path:
        try:
            os.remove(path)
        except OSError:
            pass


def remove_dir(user_id, rel_dir: str) -> None:
    full = safe_join(user_root(user_id), rel_dir)
    if full and os.path.isdir(full):
        shutil.rmtree(full, ignore_errors=True)


def delete_user_media(user_id, keep_avatar: bool = True) -> None:
    """Wipe a user's series, issue and entity images."""
    for rel in (SERIES_DIR, ENTITIES_DIR) + (() if keep_avatar else (AVATAR_DIR,)):
        remove_dir(user_id, rel)

    init_user_dirs(user_id)
