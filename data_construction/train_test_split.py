import json
import random
from sklearn.model_selection import train_test_split

def split_json_file(input_file, train_file, test_file, test_size=0.2, random_seed=42):
    # JSON 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    
    # 데이터 셔플링 및 분할
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_seed)
    
    # 분할된 데이터 저장
    with open(train_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(train_data, jsonfile, indent=4)

    with open(test_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(test_data, jsonfile, indent=4)

    print(f"Data split complete: {len(train_data)} training samples, {len(test_data)} test samples.")
    print(f"Training data saved to {train_file}")
    print(f"Test data saved to {test_file}")

# JSON 파일 경로 설정
input_file = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed/Conversations_PubMed.json'
train_file = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed/Conversations_PubMed_train.json'
test_file = '/home/hb0522/MLLM/MLLM1/JSONs/pubmed/Conversations_PubMed_test.json'

# JSON 파일 분할 및 저장
split_json_file(input_file, train_file, test_file, test_size=0.2, random_seed=42)
