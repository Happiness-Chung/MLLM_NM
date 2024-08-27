import pandas as pd
import json

# CSV 파일을 읽어옵니다.
file_path = '/home/hb0522/MLLM/MLLM2/csv/hecktor2021_3d.csv'
df = pd.read_csv(file_path)

# 설명을 생성하는 함수
def generate_description(row):
    description = []

    # Modality에 따른 설명 추가
    if row['modality'] == 'PET':
        description.append(f"The image appears to be a PET scan using {row['tracer']} as the tracer.")
    elif row['modality'] == 'CT':
        description.append("The image appears to be a CT scan.")

    # Region 설명 추가
    if row['region'] == 'head and neck':
        description.append("It shows the head and neck region of the patient.")
    elif row['region'] == 'whole body':
        description.append("It shows the whole body of the patient.")

    # Gender 설명 추가 (whole body인 경우에만)
    if row['region'] == 'whole body':
        if row['gender'] == 'M':
            description.append("The patient appears to be male.")
        elif row['gender'] == 'F':
            description.append("The patient appears to be female.")

    # Disease 설명 추가
    description.append(f"The patient has tumors located in the head and neck region.")

    # TNM 설명 추가 (head and neck cancer 기준)
    if pd.notnull(row['T-stage']):
        if row['T-stage'] == 'T1':
            description.append("The T-stage is T1, indicating a small tumor (≤2 cm) that is limited to the organ of origin and has not spread to nearby tissues.")
        elif row['T-stage'] == 'T2':
            description.append("The T-stage is T2, indicating a tumor size between 2 cm and 4 cm, or slight extension into nearby areas, but still limited to the region of origin.")
        elif row['T-stage'] == 'T3':
            description.append("The T-stage is T3, indicating a larger tumor (>4 cm) that has started to invade surrounding tissues or structures in the head and neck region.")
        elif row['T-stage'] == 'T4':
            description.append("The T-stage is T4, indicating an advanced tumor that has grown into nearby structures such as bone, muscles, or other parts of the neck or head, potentially affecting function and prognosis.")
    
    if pd.notnull(row['N-stage']):
        if row['N-stage'] == 'N0':
            description.append("The N-stage is N0, indicating no regional lymph node metastasis.")
        elif row['N-stage'] == 'N1':
            description.append("The N-stage is N1, indicating metastasis to a single ipsilateral lymph node, 3 cm or less in greatest dimension.")
        elif row['N-stage'] == 'N2':
            description.append("The N-stage is N2, indicating metastasis to a single ipsilateral lymph node between 3 cm and 6 cm, or multiple ipsilateral lymph nodes, none more than 6 cm in greatest dimension.")
        elif row['N-stage'] == 'N2a':
            description.append("The N-stage is N2a, indicating metastasis to a single ipsilateral lymph node, between 3 cm and 6 cm in greatest dimension.")
        elif row['N-stage'] == 'N2b':
            description.append("The N-stage is N2b, indicating metastasis to multiple ipsilateral lymph nodes, none more than 6 cm in greatest dimension.")
        elif row['N-stage'] == 'N2c':
            description.append("The N-stage is N2c, indicating metastasis to bilateral or contralateral lymph nodes, none more than 6 cm in greatest dimension.")
        elif row['N-stage'] == 'N3':
            description.append("The N-stage is N3, indicating metastasis in a lymph node more than 6 cm in greatest dimension.")

    # M-stage 및 TNM 그룹 설명 추가 (head and neck region에서도 M1인 경우와 whole body와 동일하게 처리)
    if pd.notnull(row['M-stage']):
        if row['M-stage'] == 'M0':
            description.append("The M-stage is M0, indicating that there is no distant metastasis, meaning the cancer has not spread to other parts of the body.")
            if row['region'] == 'head and neck':
                description.append("Currently, no metastasis is visible in the scanned region.")
        elif row['M-stage'] == 'M1':
            description.append("The M-stage is M1, indicating that distant metastasis is present, meaning the cancer has spread to other parts of the body.")
    
    # TNM group 설명 (M1인 경우 head and neck에서도 처리)
    if (row['region'] == 'whole body' or (row['region'] == 'head and neck' and row['M-stage'] == 'M1')) and pd.notnull(row['TNM group']):
        if row['TNM group'] == 'I':
            description.append("The TNM group is I, indicating early-stage cancer with a small tumor, no regional lymph node involvement, and no distant metastasis.")
            # description.append("The patient might not experience noticeable symptoms, but slight discomfort or unusual feelings in the neck may occur.")
        elif row['TNM group'] == 'II':
            description.append("The TNM group is II, indicating a slightly larger tumor or minimal regional lymph node involvement, but no distant metastasis.")
            # description.append("The patient might experience discomfort or pain in the neck, especially during swallowing or speaking. A lump in the neck might also be noticed.")
        elif row['TNM group'] == 'III':
            description.append("The TNM group is III, indicating a larger tumor and/or significant regional lymph node involvement, but no distant metastasis.")
            # description.append("The patient might experience noticeable symptoms such as difficulty swallowing, persistent throat pain, hoarseness, and possibly a lump or swelling in the neck.")
        elif row['TNM group'] == 'IV':
            description.append("The TNM group is IV, indicating a very advanced tumor with extensive local spread and/or lymph node involvement, but no distant metastasis.")
            # description.append("The patient might experience severe symptoms including intense pain, difficulty swallowing, breathing difficulties, weight loss, and significant fatigue.")
        elif row['TNM group'] == 'IVA':
            description.append("The TNM group is IVA, indicating a very advanced tumor with significant local invasion and/or regional lymph node involvement, but no distant metastasis.")
            # description.append("The patient might experience similar symptoms to Group IV, with potential facial or neck deformities, bleeding, and severe difficulty in swallowing.")
        elif row['TNM group'] == 'IVB':
            description.append("The TNM group is IVB, indicating an advanced tumor that may have spread extensively to lymph nodes or nearby structures without distant metastasis.")
            # description.append("The patient might experience extreme pain, breathing difficulties, and possible nerve damage leading to paralysis or sensory loss.")
        elif row['TNM group'] == 'IVC':
            description.append("The TNM group is IVC, indicating the presence of distant metastasis, with cancer spread to other parts of the body, which is associated with a poor prognosis.")
            # description.append("The patient might experience systemic symptoms such as weight loss, fatigue, and specific symptoms depending on the site of metastasis, like shortness of breath or jaundice.")

    # 최종 설명을 연결하여 반환
    return ' '.join(description)

# JSON 데이터를 생성하는 함수
def create_json_description(df):
    descriptions = []

    for _, row in df.iterrows():
        description = generate_description(row)
        entry = {
            "ID": f"{row['modality']}/{row['id']}.nii.gz",
            "Description": description
        }
        descriptions.append(entry)

    return descriptions

# JSON 데이터 생성
json_data = create_json_description(df)

# JSON 파일로 저장
output_json_path = '/home/hb0522/MLLM/MLLM2/Description/Descriptions_hector3D_2.json'
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4)

print(f"JSON descriptions saved to {output_json_path}")
