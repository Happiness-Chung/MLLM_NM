import os
from PIL import Image
import numpy as np
from tqdm import tqdm

def resize_and_pad_image(image, size=(224, 224), pad_color=(0, 0, 0)):
    """
    이미지를 비율을 유지하면서 주어진 크기로 변환하고, 비어있는 부분을 패딩 처리합니다.
    """
    original_size = image.size
    ratio = min(size[0] / original_size[0], size[1] / original_size[1])
    new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

    # 새 캔버스 생성 (패딩 포함)
    new_image = Image.new("RGB", size, pad_color)
    new_image.paste(resized_image, ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2))
    
    return new_image

def process_images(input_folder, output_folder):
    """
    지정된 폴더에서 'ECT' 키워드를 포함한 이미지를 찾아서 224x224로 변환 후 저장합니다.
    """
    # 입력 폴더에 있는 이미지 파일들 처리
    for filename in tqdm(os.listdir(input_folder), desc="Processing images"):
        if 'ECT' in filename:
            # 이미지 열기
            image_path = os.path.join(input_folder, filename)
            try:
                with Image.open(image_path) as img:
                    # 이미지 변환 및 패딩
                    resized_img = resize_and_pad_image(img)
                    
                    # 저장할 경로 설정
                    save_path = os.path.join(output_folder, filename)
                    resized_img.save(save_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# 폴더 경로 설정
input_folder = '/mnt/d/Archive/Data/MLLM/images/2D/PubMed'
output_folder = '/mnt/d/Archive/Data/MLLM/images/2D/PubMed'

# 출력 폴더 생성
os.makedirs(output_folder, exist_ok=True)

# 이미지 처리 및 저장
process_images(input_folder, output_folder)

print("All images have been processed and saved.")
