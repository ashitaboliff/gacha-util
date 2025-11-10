import os
from PIL import Image
import config

# ======== 設定 ========
target_width = 600           # 出力する幅（px）
quality = 80                 # WebP品質（0〜100）
# =====================


def convert_png_to_webp(input_path, output_path):
    """単一ファイルをWebPに変換"""
    with Image.open(input_path) as img:
        w, h = img.size
        ratio = target_width / w
        target_height = int(h * ratio)
        img_resized = img.resize((target_width, target_height), Image.LANCZOS)
        img_resized.save(output_path, "WEBP", quality=quality, method=6)
    print(f"Converted: {input_path} → {output_path}")


def convert_directory(input_folder=None, output_folder=None):
    """input_folder 配下の PNG/JPEG を WebP に一括変換"""
    source_root = input_folder or config.input_folder
    destination_root = output_folder or config.output_folder

    for root, dirs, files in os.walk(source_root):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, source_root)
                output_subdir = os.path.join(destination_root, rel_path)
                os.makedirs(output_subdir, exist_ok=True)
                output_path = os.path.join(output_subdir, os.path.splitext(file)[0] + ".webp")
                convert_png_to_webp(input_path, output_path)

    print("✅ すべてのPNGをWebPに変換しました。")


if __name__ == "__main__":
    convert_directory()
