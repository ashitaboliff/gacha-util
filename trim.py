from PIL import Image
import os
import config

# フォルダ内のすべてのPNG画像を処理
for filename in os.listdir(config.input_folder):
    if filename.lower().endswith('.png'):
        input_path = os.path.join(config.input_folder, filename)
        output_path = os.path.join(config.output_folder, filename)
        
        # 画像を開く
        with Image.open(input_path) as img:
            # アルファチャンネルを考慮してトリミング
            trimmed_img = img.crop(img.getbbox())
            
            # トリミングした画像を保存
            trimmed_img.save(output_path)
            print(f"Processed: {filename}")
