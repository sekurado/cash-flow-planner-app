#!/usr/bin/env python3
"""Generate platform packaging icons from resources/icons/app-icon.svg."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "resources" / "icons" / "app-icon.svg"
OUT_DIR = ROOT / "resources" / "icons"

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)

# iconutil iconset mapping: filename -> pixel size
ICNS_ICONSET: dict[str, int] = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def render_svg_to_image(renderer: QSvgRenderer, size: int) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image


def qimage_to_pil(image: QImage) -> Image.Image:
    rgba = image.convertToFormat(QImage.Format.Format_RGBA8888)
    width = rgba.width()
    height = rgba.height()
    bytes_per_line = rgba.bytesPerLine()
    row_bytes = width * 4
    size_in_bytes = rgba.sizeInBytes()

    buffer = rgba.constBits()
    if hasattr(buffer, "setsize"):
        buffer.setsize(size_in_bytes)
        raw = bytes(buffer)
    else:
        raw = buffer.tobytes()[:size_in_bytes]

    if bytes_per_line == row_bytes:
        data = raw[: height * row_bytes]
    else:
        data = bytearray()
        for row in range(height):
            start = row * bytes_per_line
            data.extend(raw[start : start + row_bytes])

    return Image.frombytes("RGBA", (width, height), bytes(data))


def write_ico(renderer: QSvgRenderer, output_path: Path) -> None:
    images = [qimage_to_pil(render_svg_to_image(renderer, size)) for size in ICO_SIZES]
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(size, size) for size in ICO_SIZES],
        append_images=images[1:],
    )


def write_icns(renderer: QSvgRenderer, output_path: Path) -> None:
    iconutil = shutil.which("iconutil")
    if iconutil is None:
        print("warning: iconutil not found — skipping app-icon.icns", file=sys.stderr)
        return

    with tempfile.TemporaryDirectory(prefix="app-icon-") as tmp_dir:
        iconset_dir = Path(tmp_dir) / "app-icon.iconset"
        iconset_dir.mkdir()

        for filename, size in ICNS_ICONSET.items():
            png_path = iconset_dir / filename
            qimage_to_pil(render_svg_to_image(renderer, size)).save(png_path, format="PNG")

        subprocess.run(
            [iconutil, "-c", "icns", str(iconset_dir), "-o", str(output_path)],
            check=True,
        )


def main() -> int:
    if not SVG_PATH.is_file():
        print(f"error: source icon not found: {SVG_PATH}", file=sys.stderr)
        return 1

    _ = QGuiApplication(sys.argv)
    renderer = QSvgRenderer(str(SVG_PATH))
    if not renderer.isValid():
        print(f"error: invalid SVG: {SVG_PATH}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ico_path = OUT_DIR / "app-icon.ico"
    write_ico(renderer, ico_path)
    print(f"Created {ico_path}")

    icns_path = OUT_DIR / "app-icon.icns"
    write_icns(renderer, icns_path)
    if icns_path.is_file():
        print(f"Created {icns_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
