import json

def create_conversations(item):
    # Description을 사용하여 대화 생성
    conversations = [
        {
            "from": "human",
            "value": "Please describe this image."
        },
        {
            "from": "gpt",
            "value": item['Description']
        }
    ]
    
    return {
        "id": f"{item['ID']}",
        "image": f"{item['ID']}.jpg",
        "conversations": conversations
    }

def process_items(input_filename, output_filename):
    # JSON 파일 읽기
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_conversations = []

    # 각 아이템에 대해 대화 생성
    for item in data:
        conversation = create_conversations(item)
        all_conversations.append(conversation)

    # 생성된 대화를 JSON 파일에 저장
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_conversations, f, indent=4)

    print(f"Conversations saved to {output_filename}")

# JSON 파일 경로 설정
input_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed_final.json'  # 입력 JSON 파일 경로
output_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Conversations_PubMed.json'  # 출력 JSON 파일 경로

# JSON 파일 처리 및 생성
process_items(input_filename, output_filename)
