import json
import random

# JSON 파일을 읽어옵니다.
input_file_path = '/home/hb0522/MLLM/MLLM2/Description/Descriptions_hector3D_2.json'
output_file_path = '/home/hb0522/MLLM/MLLM2/Description/Conversations_hector3D.json'

# JSON 파일을 로드합니다.
with open(input_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def create_conversations(item):
    description = item["Description"]
    
    # 첫 질문 리스트
    first_questions = [
        "Can you describe what is shown in this image?\n<image>",
        "What do you see in this image?\n<image>",
        "Please explain the contents of this image.\n<image>",
        "What is depicted in this image?\n<image>",
        "Could you provide a description of this image?\n<image>"
    ]
    
    # 첫 질문을 무작위로 선택
    first_question = random.choice(first_questions)
    
    # 각 부분을 대화 형식으로 분리합니다.
    sections = description.split('. ')
    sections = [section.strip() for section in sections if section]  # 빈 문자열 제거
    
    # 질문과 답변을 생성합니다.
    conversations = [
        {
            "from": "human",
            "value": first_question
        },
        {
            "from": "gpt",
            "value": sections[0] + "."
        }
    ]

    # 각 설명에 대해 추가 질문과 답변을 추가합니다.
    for section in sections[1:]:
        if "PET scan" in section or "CT scan" in section:
            question = "What type of scan is this?"
        elif "whole body" in section or "head and neck" in section:
            question = "Which region of the body is shown in the image?"
        elif "tumor" in section:
            question = "Are there any tumors present in the image?"
        elif "T-stage" in section:
            question = "What is the T-stage of the patient?"
        elif "N-stage" in section:
            question = "What is the N-stage of the patient?"
        elif "M-stage" in section:
            question = "What is the M-stage of the patient?"
        elif "TNM group" in section:
            question = "What is the TNM group of the patient?"
        else:
            continue  # 매칭되지 않는 경우 질문을 건너뜁니다.

        conversations.append({
            "from": "human",
            "value": question
        })
        conversations.append({
            "from": "gpt",
            "value": section + "."
        })
    
    # 최종 대화 구조 생성
    return {
        "id": item["ID"],
        "image": item["ID"],
        "conversations": conversations
    }

# 새로운 JSON 파일을 생성합니다.
output_data = []
for item in data:
    conversation = create_conversations(item)
    output_data.append(conversation)

# JSON 파일로 저장합니다.
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4)

print(f"Conversations saved to {output_file_path}")
