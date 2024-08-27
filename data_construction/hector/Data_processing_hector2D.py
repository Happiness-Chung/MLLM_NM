import pandas as pd
import json

# CSV 파일을 읽어옵니다.
file_path = '/home/hb0522/MLLM/MLLM2/csv/hecktor2021_2d.csv'
df = pd.read_csv(file_path)


def generate_description(row):
    description = []

    # Modality에 따른 설명 추가
    if row['modality'] == 'PET':
        description.append(f"The image appears to be a PET scan using {row['tracer']} as the tracer.")
    elif row['modality'] == 'CT':
        description.append("The image appears to be a CT scan.")
    else:
        description.append(f"The image appears to be a PET/CT scan using {row['tracer']} as the tracer.")

    # Region 설명 추가
    if row['region'] == 'head and neck':
        description.append("It shows the head and neck region of the patient.")
    elif row['region'] == 'whole body':
        description.append("It shows the whole body of the patient.")

    # Tumor 설명 추가
    if row['tumor'] == 'absent':
        description.append(f"No tumors are present in this slice.")
    else:
        description.append(f"Tumors are present in this slice.")
        
    # 최종 설명을 연결하여 반환
    return ' '.join(description)

# JSON 데이터를 생성하는 함수
def create_json_description(df):
    descriptions = []
    modalities = ['PET_CT_hot', 'PET_CT_jet', 'PET_hot', 'PET_inverse', 'PET_jet', 'PET_original', 'CT']

    for _, row in df.iterrows():
        description = generate_description(row)
        if row['modality'] == 'CT':
            entry = {
                "ID": f"{row['modality']}/{row['file']}",
                "Description": description
            }
            descriptions.append(entry)
        else:
            for m in range(len(modalities)):
                entry = {
                "ID": f"{modalities[m]}/{row['file']}",
                "Description": description
                }
                descriptions.append(entry)
        

    return descriptions

# JSON 데이터 생성
json_data = create_json_description(df)

# JSON 파일로 저장
output_json_path = '/home/hb0522/MLLM/MLLM2/Description/Descriptions_hector2D.json'
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4)

print(f"JSON descriptions saved to {output_json_path}")