import os
from PIL import Image

# ======== 設定 ========
input_dir = "input"   # PNGファイルがあるルートディレクトリ
output_dir = "output"   # 出力ルートディレクトリ
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

# 再帰的に処理
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(".png"):
            # 入力ファイルパス
            input_path = os.path.join(root, file)

            # 相対パス（input_dir からの相対位置）
            rel_path = os.path.relpath(root, input_dir)

            # 出力先ディレクトリとファイルパス
            output_subdir = os.path.join(output_dir, rel_path)
            os.makedirs(output_subdir, exist_ok=True)
            output_path = os.path.join(output_subdir, os.path.splitext(file)[0] + ".webp")

            # 変換
            convert_png_to_webp(input_path, output_path)

print("✅ すべてのPNGをWebPに変換しました。")
