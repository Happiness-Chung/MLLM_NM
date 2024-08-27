import json
from tqdm import tqdm

def create_conversation(row, index):
    image_id = row["ID"]
    description = row["Description"]
    
    # Modality 정보 추출
    if "PET scan" in description:
        modality = "PET scan using 18F-FDG as the tracer."
    elif "CT scan" in description:
        modality = "CT scan."
        contrast_agent = "A contrast agent was used in this scan." if "contrast agent" in description else "No contrast agent was used."
    else:
        modality = "PET/CT scan using 18F-FDG as the tracer."

    # Region 정보 추출
    if "head and neck" in description:
        region = "head and neck region"
    elif "whole body" in description:
        region = "whole body"
    else:
        region = "unknown region"

    # Tumor 존재 여부 및 질병 정보 추출
    if "No tumors are present" in description:
        tumor_presence = "No tumors are present in this slice."
        disease_info = None
    else:
        tumor_presence = "Tumors are present in this slice."
        if "The patient could be diagnosed with" in description:
            disease_info = description.split("The patient could be diagnosed with")[1].strip()
        else:
            disease_info = None

    # 대화 생성
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

    # CT scan인 경우 조영제에 대해 묻는 질문 추가
    if "CT scan" in modality:
        conversations.append({
            "from": "human",
            "value": "Was a contrast agent used in this scan?"
        })
        conversations.append({
            "from": "gpt",
            "value": contrast_agent
        })
    
    # Tumor가 있는 경우 질병에 대해 묻는 질문 추가
    if disease_info:
        conversations.append({
            "from": "human",
            "value": "What disease could the patient be diagnosed with?"
        })
        conversations.append({
            "from": "gpt",
            "value": f"The patient could be diagnosed with {disease_info}."
        })
    
    return {
        "id": f"AutoPET{index}",
        "image": image_id,
        "conversations": conversations
    }

def process_descriptions(input_file, output_file, start_id=None, save_every=500):
    with open(input_file, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    with open('/home/hb0522/MLLM/MLLM2/Description/Conversations_autoPET2D.json', 'r', encoding='utf-8') as jsonfile:
        exist = json.load(jsonfile)
        start_index = len(exist)

    with open('/home/hb0522/MLLM/MLLM2/Description/Conversations_autoPET2D_2.json', 'r', encoding='utf-8') as jsonfile:
        exist = json.load(jsonfile)
        start_index += len(exist)

    with open('/home/hb0522/MLLM/MLLM2/Description/Conversations_autoPET2D_3.json', 'r', encoding='utf-8') as jsonfile:
        exist = json.load(jsonfile)
        start_index += len(exist)

    all_conversations = []

    start_processing = False if start_id else True
    start_processing = True

    for index, row in enumerate(tqdm(data[start_index:]), start=1):
        # if start_id and row["ID"] == start_id:
        #     start_processing = True
        #     continue
        
        if start_processing:
            conversation = create_conversation(row, index)
            all_conversations.append(conversation)

            # Save every `save_every` items
            if index % save_every == 0:
                with open(output_file, 'w', encoding='utf-8') as jsonfile:
                    json.dump(all_conversations, jsonfile, indent=4)

    # Final save after all items are processed
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_conversations, jsonfile, indent=4)

    print(f"Conversations saved to {output_file}")

# JSON 파일 경로 설정
input_file = '/home/hb0522/MLLM/MLLM2/Description/Descriptions_autoPET2D.json'
output_file = '/home/hb0522/MLLM/MLLM2/Description/Conversations_autoPET2D_4.json'
start_id = 'PET_CT_jet/fdg_0143bab87a_07-17-2005-NA-PET-CT Ganzkoerper  primaer mit KM-33529_sagittal_121_absent.jpg'  # 여기서부터 시작

# JSON 파일 처리 및 JSON 파일 생성
process_descriptions(input_file, output_file, start_id, save_every=2000)

print(f"Conversations saved to {output_file}")
