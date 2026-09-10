from PIL import Image


def dominant_color(path: str) -> str:
    """Return the dominant colour of an image as the string (R,G,B)"""

    def brighten(color):
        return [c + 50 if 100 < c < 150 else c for c in color]

    with Image.open(path) as im:
        img = im.convert("RGB")
        img.thumbnail((100, 100))
        paletted = img.convert("P", palette=Image.ADAPTIVE, colors=16)
        palette = paletted.getpalette()
        counts = sorted(paletted.getcolors(), reverse=True)

    fallback = None
    for _, index in counts:
        color = palette[index * 3:index * 3 + 3]
        if fallback is None:
            fallback = color
        if any(c > 100 for c in color):
            color = brighten(color)
            return f"({color[0]},{color[1]},{color[2]})"
    color = fallback or [0, 0, 0]
    return f"({color[0]},{color[1]},{color[2]})"
