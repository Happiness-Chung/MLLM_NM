import json

# JSON 파일을 읽어옵니다.
input_json_path = '/root/MLLM/LLaVA-NeXT/Data/Conversations_PubMed_test.json'
output_txt_path = '/root/MLLM/LLaVA-NeXT/results/labels.txt'

# JSON 파일을 열고 데이터를 로드합니다.
with open(input_json_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 텍스트 파일을 작성합니다.
with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
    for item in data:
        conversations = item["conversations"]
        conversation_text = ""
        
        for conversation in conversations:
            if conversation["from"] == "human":
                conversation_text += "USER: " + conversation["value"] + " "
            elif conversation["from"] == "gpt":
                conversation_text += "ASSISTANT: " + conversation["value"] + " "
        
        # 대화 끝에 구분자 \n\n\n을 추가합니다.
        txt_file.write(conversation_text.strip() + "\n\n\n")

print(f"Text file saved to {output_txt_path}")
