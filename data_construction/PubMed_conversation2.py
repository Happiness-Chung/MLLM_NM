import json
import random
from openai import OpenAI
from tqdm import tqdm

# OpenAI API 키 설정
# client = OpenAI(
#     api_key=
# )

def create_conversation(item):
    description = item['Description']
    image_id = item['ID']

    # 다양한 첫 질문 리스트, <image> 토큰 추가
    first_questions = [
        "Can you describe the image for me?\n<image>",
        "What do you see in this image?\n<image>",
        "Please explain what is shown in the image.\n<image>",
        "Could you provide a description of this image?\n<image>",
        "What is depicted in this image?\n<image>"
    ]

    # 첫 질문을 무작위로 선택
    first_question = random.choice(first_questions)

    # 초기 프롬프트 생성
    prompt = f"""
    Based on the following description, generate a series of conversational exchanges between a human and an AI:
    
    Description: {description}
    
    The conversation should begin with the human asking, "{first_question}"
    Then, create appropriate follow-up questions and answers to delve deeper into the contents and context of the image.
    """

    try:
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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

        # GPT의 응답을 추출하고 JSON 형식으로 반환
        conversation_text = response.choices[0].message.content.strip()
        
        # 대화 내용을 구조화된 JSON으로 변환
        conversations = []
        lines = conversation_text.split("\n")
        for line in lines:
            if line.startswith("Human:"):
                conversations.append({"from": "human", "value": line.replace("Human:", "").strip()})
            elif line.startswith("AI:"):
                conversations.append({"from": "gpt", "value": line.replace("AI:", "").strip()})

        return {
            "id": image_id,
            "image": f"{image_id}.jpg",
            "conversations": conversations
        }

    except Exception as e:
        print(f"Error generating conversation for ID {image_id}: {e}")
        return None

def process_items(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_conversations = []

    for item in tqdm(data, desc="Generating conversations"):
        conversation = create_conversation(item)
        if conversation:
            all_conversations.append(conversation)

        # JSON 파일을 순차적으로 저장
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_conversations, f, indent=4)

    print(f"Conversations saved to {output_filename}")

# JSON 파일 경로 설정
input_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_PubMed_final.json'
output_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Conversations_PubMed2.json'

# JSON 파일 처리 및 대화 생성
process_items(input_filename, output_filename)
