from PIL import Image
import os

# トリミングするフォルダのパス
input_folder = "gacha"  # PNG画像が保存されているフォルダ
output_folder = "output_folder"  # トリミング後の画像を保存するフォルダ

# フォルダが存在しない場合は作成
os.makedirs(output_folder, exist_ok=True)

# フォルダ内のすべてのPNG画像を処理
for filename in os.listdir(input_folder):
    if filename.lower().endswith('.png'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # 画像を開く
        with Image.open(input_path) as img:
            # アルファチャンネルを考慮してトリミング
            trimmed_img = img.crop(img.getbbox())
            
            # トリミングした画像を保存
            trimmed_img.save(output_path)
            print(f"Processed: {filename}")
