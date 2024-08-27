import json
from tqdm import tqdm

def generate_conversations(row, index):
    image_id = row["ID"]
    description = row["Description"]
    
    # 이미지 타입 판별
    if "PET_CT" in image_id:
        image_type = "This image is the fusion of FDG-PET and CT."
    else:
        image_type = "This image is the FDG-PET."

    gender = "male" if "male patient" in description else "female"
    age_range = description.split("appears to be between ")[1].split(".")[0]
    tumor = "appears to have tumors" in description
    if tumor:
        t_stage = description.split("T-stage is ")[1].split(".")[0]
        n_stage = description.split("N-stage is ")[1].split(",")[0]
        m_stage = description.split("M-stage is ")[1].split(".")[0]
        hpv_status = "HPV positive" if "HPV positive" in description else "HPV negative"

    # 전체 설명 및 개별 정보에 대한 대화
    conversations = [
        {
            "from": "human",
            "value": "Please describe this image.\n<image>"
        },
        {
            "from": "gpt",
            "value": description
        },
        {
            "from": "human",
            "value": "What type of image is this?"
        },
        {
            "from": "gpt",
            "value": image_type
        },
        {
            "from": "human",
            "value": "What is the sex of the patient?"
        },
        {
            "from": "gpt",
            "value": f"The patient in the image seems {gender}."
        },
        {
            "from": "human",
            "value": "What is the age range of the patient?"
        },
        {
            "from": "gpt",
            "value": f"The patient's age appears to be {age_range}."
        }
    ]
    
    if tumor:
        conversations.extend([
            {
                "from": "human",
                "value": "Does the patient have tumors?"
            },
            {
                "from": "gpt",
                "value": "The patient appears to have tumors."
            },
            {
                "from": "human",
                "value": "What is the T-stage of the patient?"
            },
            {
                "from": "gpt",
                "value": f"The patient's T-stage is {t_stage}."
            },
            {
                "from": "human",
                "value": "What is the N-stage of the patient?"
            },
            {
                "from": "gpt",
                "value": f"The patient's N-stage is {n_stage}."
            },
            {
                "from": "human",
                "value": "What is the M-stage of the patient?"
            },
            {
                "from": "gpt",
                "value": f"The patient's M-stage is {m_stage}."
            },
            {
                "from": "human",
                "value": "What is the HPV status of the patient?"
            },
            {
                "from": "gpt",
                "value": f"The patient is {hpv_status}."
            }
        ])
    else:
        conversations.extend([
            {
                "from": "human",
                "value": "Does the patient have tumors?"
            },
            {
                "from": "gpt",
                "value": "The patient appears healthy."
            }
        ])
    
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
        all_conversations.append(conversation)
    
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_conversations, jsonfile, indent=4)

# JSON 파일 경로 설정
input_file = '/home/hb0522/MLLM/MLLM2/hector_descriptions.json'
output_file = '/home/hb0522/MLLM/MLLM2/conversations.json'

# JSON 파일 처리 및 JSON 파일 생성
process_descriptions(input_file, output_file)

print(f"Conversations saved to {output_file}")
