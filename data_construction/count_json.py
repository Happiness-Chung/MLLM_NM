import json

def count_json_elements(file_path):
    # JSON 파일 읽기
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # 최상위 요소의 갯수 반환
    return len(data)

# 사용 예시
file_path = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed/Conversations_PubMed_test.json'  # JSON 파일의 경로를 지정하세요
element_count = count_json_elements(file_path)
print(f"JSON 파일 내 요소의 갯수: {element_count}")
