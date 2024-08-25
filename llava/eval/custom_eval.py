from transformers import AutoTokenizer, CLIPProcessor, CLIPModel
from transformers import CLIPVisionModel, CLIPImageProcessor, CLIPVisionConfig
from llava.constants import IGNORE_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN, IMAGE_TOKEN_INDEX
from llava import LlavaLlamaForCausalLM
import torch
from PIL import Image

def feature_select(image_forward_outs):
        
        select_feature = getattr(args, "mm_vision_select_feature", "patch")

        select_feature_type = select_feature

        if select_feature in ["slicefour_patch", "slicefour_cls_patch"]:
            select_every_k_layer = len(image_forward_outs.hidden_states) // 4
            image_features = torch.cat([image_forward_outs.hidden_states[i] for i in range(select_every_k_layer + self.select_layer, len(image_forward_outs.hidden_states), select_every_k_layer)], dim=-1)
            select_feature_type = select_feature_type.replace("slicefour_", "")
        elif select_feature in ["slice_m25811_f6_patch", "slice_m25811_f6_cls_patch"]:
            select_layers = [-2, -5, -8, -11, 6]
            image_features = torch.cat([image_forward_outs.hidden_states[i] for i in select_layers], dim=-1)
            select_feature_type = select_feature_type.replace("slice_m25811_f6_", "")
        else:
            image_features = image_forward_outs.hidden_states[self.select_layer]

        if select_feature_type == "patch":
            image_features = image_features[:, 1:]
        elif select_feature_type == "cls_patch":
            image_features = image_features
        else:
            raise ValueError(f"Unexpected select feature: {select_feature_type}")
        return image_features

# 모델과 토크나이저 경로
model_path = "lmsys/vicuna-7b-v1.5"

# 토크나이저 로드 및 이미지 토큰 추가
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 모델 로드 및 토크나이저 업데이트
model = LlavaLlamaForCausalLM.from_pretrained(model_path)

# 필요한 경우, 어댑터 모델과 non_lora_trainables를 로드
adapter_model_path = "/root/MLLM/LLaVA-NeXT/results/adapter_model.bin"
non_lora_trainables_path = "/root/MLLM/LLaVA-NeXT/results/non_lora_trainables.bin"

# 어댑터 모델 로드
adapter_state_dict = torch.load(adapter_model_path, map_location=torch.device('cpu'))
model.load_state_dict(adapter_state_dict, strict=False)

# non-lora trainables 로드
non_lora_state_dict = torch.load(non_lora_trainables_path, map_location=torch.device('cpu'))
model.load_state_dict(non_lora_state_dict, strict=False)

# 모델을 GPU로 이동 (필요 시)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 모델을 평가 모드로 전환
model.eval()

# 예제 이미지와 텍스트 입력
image = Image.open("/root/MLLM/LLaVA-NeXT/Data/hector2021/PET_CT_hot/CHGJ007_axial_98_absent.jpg").convert("RGB")
text = "Please describe this image.\n<image>"

# 이미지 임베딩 생성 (CLIP 모델을 사용하여)
# vision_tower_path = "openai/clip-vit-base-patch32"
# processor = CLIPImageProcessor.from_pretrained(vision_tower_path)
# vision_tower = model.get_vision_tower()
# vision_tower.to(dtype=torch.bfloat16)
# vision_tower = CLIPVisionModel.from_pretrained(vision_tower_path)

image = Image.open("/root/MLLM/LLaVA-NeXT/Data/hector2021/PET_CT_hot/CHGJ007_axial_98_absent.jpg").convert("RGB")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
image_input = processor(images=image, return_tensors="pt").pixel_values.to(device)

# 이미지를 전처리하고 CLIP 모델을 통해 이미지 임베딩 생성
# inputs = processor(images=image, return_tensors="pt")
# image_forward_outs = vision_tower(**inputs, output_hidden_states=True)
# image_embeddings = feature_select(image_forward_outs)

# 텍스트 입력 처리
# text_inputs = tokenizer(text, return_tensors="pt")
question_input = tokenizer(text, return_tensors="pt").to(device)
# 모델 입력을 결합
position_ids = torch.arange(question_input["input_ids"].size(-1), dtype=torch.long, device=question_input["input_ids"].device).unsqueeze(0).expand(question_input["input_ids"].size(0), -1)
# 모델 예측

print(question_input["input_ids"])

with torch.no_grad():
    outputs = model.generate(
        inputs=question_input["input_ids"],
        position_ids=position_ids,
        attention_mask=question_input["attention_mask"],
        images=image_input,  # 이미지 입력 추가
        image_sizes = [224, 224]
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("Generated Text:", generated_text)

import matplotlib.pyplot as plt

# 이미지와 예측 결과를 시각화
plt.figure(figsize=(10, 5))
plt.imshow(image)
plt.title(f"Question: {text}\nAnswer: {generated_text}")
plt.axis("off")
plt.show()