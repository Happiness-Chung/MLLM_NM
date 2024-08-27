import os
import json

def merge_json_files(input_dir, output_file):
    merged_data = []

    # 디렉토리 내의 모든 파일을 가져옴
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.extend(data)

    # 병합된 데이터를 새로운 JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4)

    print(f"Merged JSON saved to {output_file}")

# 입력 디렉토리와 출력 파일 경로 설정
input_dir = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed'
output_file = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed/Conversations_PubMed.json'

# JSON 파일 병합
merge_json_files(input_dir, output_file)
