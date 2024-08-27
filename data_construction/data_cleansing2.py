import os
import json

def filter_json_by_images(json_file, image_folder, output_file):
    # JSON 파일을 읽어옵니다.
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 이미지 폴더 내의 파일 목록을 가져옵니다.
    image_files = set(os.listdir(image_folder))

    # 이미지가 존재하는 항목만 필터링합니다.
    filtered_data = [item for item in data if f"{item['ID']}.jpg" in image_files]

    # 필터링된 데이터를 새로운 JSON 파일에 저장합니다.
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4)

    print(f"Filtered JSON saved to {output_file}")

# 경로 설정
json_file = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed_clean2.json'        # 입력 JSON 파일 경로
image_folder = '/mnt/d/Archive/Data/MLLM/images/2D/PubMed'   # 이미지 폴더 경로
output_file = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed_final.json'     # 출력 JSON 파일 경로

# 필터링 함수 실행
filter_json_by_images(json_file, image_folder, output_file)
