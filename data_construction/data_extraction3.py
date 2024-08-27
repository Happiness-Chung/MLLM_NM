import json
from tqdm import tqdm

def clean_data(input_filename, output_filename, keyword):
    # 파일에서 데이터 읽기
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 새로운 데이터 목록 초기화
    cleaned_data = []
    current_index = 1
    
    # tqdm으로 진행 상황 표시
    for item in tqdm(data, desc="Cleaning Data", unit="item"):
        url = item['Url']
        
        # 조건에 따라 데이터 추가 여부 결정
        if 'images.journals.lww.com' not in url and '/skin/' not in url:
            if '/cms/' in url:
                url = 'https://www.nejm.org' + url
                item['Url'] = url
            item['ID'] = f"{keyword}_{current_index}"
            cleaned_data.append(item)
            current_index += 1
    
    # 정리된 데이터 파일에 저장
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4)

# 변수 설정
input_filename = 'structured_data.json'
output_filename = 'cleaned_data.json'
keyword = 'LungScan'

# 데이터 정리 및 저장
clean_data(input_filename, output_filename, keyword)