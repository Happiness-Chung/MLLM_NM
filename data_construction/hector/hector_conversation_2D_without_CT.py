import json
from tqdm import tqdm

def generate_conversations(row, index):

    image_id = row["ID"]
    description = row["Description"]
    
    # Modality 정보 추출
    if "PET" in description:
        modality = "PET scan using 18F-FDG as the tracer."
    else:
        return None  # CT 스캔이 포함된 이미지는 처리하지 않음

    # Region 정보 추출
    if "head and neck" in description:
        region = "head and neck region"
    elif "whole body" in description:
        region = "whole body"
    else:
        region = "unknown region"

    # Tumor 존재 여부
    if "No tumors are present" in description or "healthy" in description:
        tumor_presence = "No tumors are present in this slice."
    else:
        tumor_presence = "Tumors are present in this slice."

    # 대화 생성
    conversations = [
        {
            "from": "human",
            "value": "Please describe this image."
        },
        {
            "from": "gpt",
            "value": description
        },
        {
            "from": "human",
            "value": "What type of scan is this?"
        },
        {
            "from": "gpt",
            "value": f"The image appears to be a {modality}"
        },
        {
            "from": "human",
            "value": "Which region of the body is shown in the image?"
        },
        {
            "from": "gpt",
            "value": f"The image shows the {region}."
        },
        {
            "from": "human",
            "value": "Are there any tumors present in the image?"
        },
        {
            "from": "gpt",
            "value": tumor_presence
        }
    ]
    
    return {
        "id": f"HECTOR{index}",
        "image": image_id,
        "conversations": conversations
    }

def process_descriptions(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    
    all_conversations = []
    for index, row in enumerate(tqdm(data), start=1):
        conversation = generate_conversations(row, index)
        if conversation is not None:  # CT 스캔 이미지는 건너뜀
            all_conversations.append(conversation)
    
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_conversations, jsonfile, indent=4)

# JSON 파일 경로 설정
input_file = '/home/hb0522/MLLM/MLLM2/Description/Descriptions_hector2D.json'
output_file = '/home/hb0522/MLLM/MLLM2/Description/Conversations_hector2D_without_CT.json'

# JSON 파일 처리 및 JSON 파일 생성
process_descriptions(input_file, output_file)

print(f"Conversations saved to {output_file}")
