import json
import re

def clean_description(description):
    # 'The image' 또는 'This image'가 문장 시작 부분에 있는 경우를 찾기
    match = re.search(r'(^|\.\s+)(The image|This image)', description)
    
    if match:
        # 'The image' 또는 'This image' 이전의 모든 텍스트와 구분자 삭제
        description = description[match.start(2):]
    # match가 없을 때는 description을 그대로 유지
    return description.strip()

def process_json(input_filename, output_filename):
    # JSON 파일 읽기
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 각 요소에 대해 Description 수정
    for item in data:
        item['Description'] = clean_description(item['Description'])

    # 수정된 JSON 파일 쓰기
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# JSON 파일 경로 설정
input_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed.json'
output_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed_clean2.json'

# JSON 파일 처리
process_json(input_filename, output_filename)

print(f"Cleaned descriptions saved to {output_filename}")
