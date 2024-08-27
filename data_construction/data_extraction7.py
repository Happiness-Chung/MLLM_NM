import os
import json
import tqdm
import openai
from openai import OpenAI

# OpenAI API 키 설정
# client = OpenAI(
#     api_key=
# )

def create_combined_description(item):
    prompt = f"""
    Title: {item['Title']}
    Abstract: {item['Abstract']}
    Caption: {item['Caption']}
    Description: {item['Description']}

    Based on the information above, create a coherent and concise description for the image, explaining its significance and context in 1-3 paragraphs. Please use almost all information related to the image. Always refer to the uploaded image as 'This image' and do not use expressions like 'Figure 1' or any other figure numbers. If the uploaded image is consisted of several sub-figures and remarked as A, B or other alphabets and there are information for each of them, please (you must) explain them respectively. If there is no respective description, explain image as one single image.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        combined_description = response.choices[0].message.content.strip()
        return {"ID": item["ID"], "Description": combined_description}

    except Exception as e:
        print(f"Error generating description for ID {item['ID']}: {e}")
        return {"ID": item["ID"], "Description": "Error generating description"}

def process_json_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_file_path = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_FDGPET_filtered.json'
    combined_descriptions = []

    # 기존 JSON 파일 로드
    with open(json_file_path, 'r', encoding='utf-8') as f:
        combined_descriptions = json.load(f)


    for item in tqdm.tqdm(data[0:], desc="Generating descriptions", initial=0, total=len(data)):
        description_result = create_combined_description(item)
        combined_descriptions.append(description_result)

        # 파일 업데이트
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(combined_descriptions, f, indent=4)

# 변수 설정
input_filename = '/home/hb0522/MLLM/MLLM1/JSONs/cleaned_data_LungScan_filtered.json'
output_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_LungScan_filtered.json'

# JSON 파일 처리
process_json_file(input_filename, output_filename)
