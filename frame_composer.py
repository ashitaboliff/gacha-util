from __future__ import annotations

import math
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

import config
import opt

BASE_DIR = Path(__file__).resolve().parent
FRAME_DIR = BASE_DIR / "lib" / "frames"
INPUT_DIR = BASE_DIR / config.input_folder
OUTPUT_DIR = BASE_DIR / config.output_folder
TEMP_DIR = OUTPUT_DIR / "_framed_png"
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg")
# 入力画像は縦長(横:縦 = 3:4)想定
EXPECTED_RATIO = 3 / 4
RATIO_TOLERANCE = 0.05
CONTENT_SCALE_RATIO = 1.0

# C.png から計測した定数（中央透過領域に数ピクセル重なるサイズ）
INNER_WIDTH_RATIO = 0.935
INNER_HEIGHT_RATIO = 0.935
INNER_LEFT_RATIO = 67 / 1559           # ≒ 0.004296
INNER_TOP_RATIO = 70 / 2078            # ≒ 0.03369


@dataclass
class FrameSpec:
    name: str
    path: Path
    bbox: tuple[int, int, int, int]
    size: tuple[int, int]


def build_frame_specs():
    specs = {}
    for frame_path in FRAME_DIR.glob("*.png"):
        with Image.open(frame_path) as frame_img:
            frame_size = frame_img.size
        bbox = derive_bbox_from_constants(frame_size)
        specs[frame_path.stem.lower()] = FrameSpec(
            name=frame_path.stem,
            path=frame_path,
            bbox=bbox,
            size=frame_size,
        )
    return specs


def derive_bbox_from_constants(size):
    width, height = size
    box_width = round(width * INNER_WIDTH_RATIO)
    box_height = round(height * INNER_HEIGHT_RATIO)
    left = round(width * INNER_LEFT_RATIO)
    top = round(height * INNER_TOP_RATIO)
    right = min(width, left + box_width)
    bottom = min(height, top + box_height)
    return (left, top, right, bottom)


def resolve_frame_key(stem, candidates):
    lowered = stem.lower()
    for key in candidates:
        if lowered == key:
            return key
        if lowered.startswith(f"{key}_") or lowered.startswith(f"{key}-"):
            return key
    return None


def ensure_ratio(image, name):
    width, height = image.size
    ratio = width / height
    if abs(ratio - EXPECTED_RATIO) > RATIO_TOLERANCE:
        print(
            f"[WARN] {name} ratio {ratio:.3f} deviates from expected 3:4."
        )


def compose_with_frame(
    base_img,
    frame_img,
    bbox,
):
    base_rgba = base_img.convert("RGBA")
    frame_rgba = frame_img.convert("RGBA")

    ensure_ratio(base_rgba, getattr(base_img, "filename", "input"))

    base_width, base_height = base_rgba.size
    box_left, box_top, box_right, box_bottom = bbox
    box_width = box_right - box_left
    box_height = box_bottom - box_top

    fit_scale = min(box_width / base_width, box_height / base_height)
    target_scale = fit_scale * CONTENT_SCALE_RATIO
    scaled_width = max(1, math.floor(base_width * target_scale))
    scaled_height = max(1, math.floor(base_height * target_scale))

    resized = base_rgba.resize((scaled_width, scaled_height), Image.LANCZOS)
    canvas = Image.new("RGBA", frame_rgba.size, (0, 0, 0, 0))

    offset_x = box_left + (box_width - scaled_width) // 2
    offset_y = box_top + (box_height - scaled_height) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)

    return Image.alpha_composite(canvas, frame_rgba)


def compose_single_image(image_path, spec, dest_png):
    with Image.open(image_path) as base_img, Image.open(spec.path) as frame_img:
        composed = compose_with_frame(base_img, frame_img, spec.bbox)
        dest_png.parent.mkdir(parents=True, exist_ok=True)
        composed.save(dest_png)
    print(f"Framed: {image_path.name} using {spec.name}.png")


def collect_input_images():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input directory not found: {INPUT_DIR}")
    return [
        path
        for path in sorted(INPUT_DIR.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def cleanup_temp(dir_path):
    if dir_path.exists():
        shutil.rmtree(dir_path)


def convert_to_webp(temp_pngs):
    for png_path in temp_pngs:
        webp_path = OUTPUT_DIR / (png_path.stem + ".webp")
        opt.convert_png_to_webp(str(png_path), str(webp_path))
        png_path.unlink(missing_ok=True)


def main():
    frame_specs = build_frame_specs()
    if not frame_specs:
        print("[ERROR] No frame assets were found under lib/frames.")
        return

    temp_outputs = []
    cleanup_temp(TEMP_DIR)

    for image_path in collect_input_images():
        frame_key = resolve_frame_key(image_path.stem, frame_specs.keys())
        if frame_key is None:
            print(f"[SKIP] No matching frame for {image_path.name}.")
            continue
        temp_png = TEMP_DIR / (image_path.stem + ".png")
        compose_single_image(image_path, frame_specs[frame_key], temp_png)
        temp_outputs.append(temp_png)

    if not temp_outputs:
        print("No images were composed. Ensure filenames include a frame prefix.")
        cleanup_temp(TEMP_DIR)
        return

    convert_to_webp(temp_outputs)
    cleanup_temp(TEMP_DIR)
    print(
        f"✅ Generated {len(temp_outputs)} framed WebP files in {OUTPUT_DIR.relative_to(BASE_DIR)}."
    )

if __name__ == "__main__":
    main()
