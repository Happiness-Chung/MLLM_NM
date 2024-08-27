import os
import json
from tqdm import tqdm

# WSL에서 Windows 디렉토리에 접근할 수 있는 경로로 변환
image_dir = "/mnt/d/Archive/Data/MLLM/images/2D/PubMed"
json_file_path = "/home/hb0522/MLLM/MLLM4/combined_descriptions.json"  # JSON 파일 경로
output_json_path = "/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_ECT_filtered.json"  # 필터링된 JSON 파일을 저장할 경로


# 이미지 파일의 확장자를 설정합니다.
image_extensions = {'.jpg'}

# 이미지 파일명을 가져옵니다.
image_files = set(os.path.splitext(f)[0] for f in os.listdir(image_dir) if os.path.splitext(f)[1].lower() in image_extensions)

# JSON 파일을 엽니다.
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 필터링된 데이터를 저장할 리스트를 초기화합니다.
filtered_data = []

# tqdm을 사용하여 루프 진행 상황을 시각화합니다.
for item in tqdm(data, desc="Filtering JSON data based on available images"):
    if item['ID'] in image_files:
        filtered_data.append(item)

# 필터링된 데이터를 새로운 JSON 파일에 저장합니다.
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtered JSON data saved to {output_json_path}")

