"""Every stored image becomes one lossy WebP, fitted to the largest size the app draws."""
import io
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageOps

try:
    from PIL import ImageCms
except ImportError:
    ImageCms = None

MAX_WIDTH, MAX_HEIGHT = 1000, 1500
QUALITY = 80
EXT = ".webp"
ACCEPTED = {"JPEG": ".jpeg", "PNG": ".png", "WEBP": ".webp", "GIF": ".gif"}

CWEBP = shutil.which(os.environ.get("VERTIGO_CWEBP", "cwebp"))


def sniff(data: bytes):
    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = img.format
            animated = bool(getattr(img, "is_animated", False))
    except Exception as exc:
        raise ValueError("not a valid image") from exc
    if fmt not in ACCEPTED:
        raise ValueError(f"unsupported image format {fmt}")
    return fmt, animated


def _srgb(img):
    icc = img.info.get("icc_profile")
    if not icc or ImageCms is None:
        return img
    try:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        return ImageCms.profileToProfile(img, src, ImageCms.createProfile("sRGB"), outputMode=img.mode)
    except (ImageCms.PyCMSError, ValueError):
        return img


def _prepare(img):
    img = ImageOps.exif_transpose(img)
    alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    img = img.convert("RGBA" if alpha else "RGB")
    scale = min(1.0, MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
    if scale < 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    return _srgb(img)


def _cwebp(img) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, "in.png"), os.path.join(tmp, "out.webp")
        img.save(src, "PNG", icc_profile=None)
        subprocess.run([CWEBP, "-quiet", "-q", str(QUALITY), "-m", "6", "-sharp_yuv", src, "-o", dst],
                       check=True, capture_output=True)
        with open(dst, "rb") as fh:
            return fh.read()


def _pillow(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=QUALITY, method=6)
    return buf.getvalue()


def to_webp(data: bytes) -> bytes:
    with Image.open(io.BytesIO(data)) as img:
        prepared = _prepare(img)
    if CWEBP:
        try:
            return _cwebp(prepared)
        except (OSError, subprocess.CalledProcessError):
            pass
    return _pillow(prepared)
