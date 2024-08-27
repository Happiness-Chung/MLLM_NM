import os
import csv
import re

# 이미지 파일이 저장된 디렉토리 경로
image_dir = '/home/hb0522/MLLM/Data/downloaded_images3'

# CSV 파일 경로
csv_file = '/home/hb0522/MLLM/Data/image_labels3.csv'

# 이미지 파일 이름을 가져옴
image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

# 파일 이름을 숫자 기준으로 정렬하는 함수
def sort_key(file_name):
    match = re.search(r'(\d+)', file_name)
    return int(match.group(1)) if match else 0

# 파일 이름 정렬
image_files.sort(key=sort_key)

# CSV 파일 생성
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # CSV 헤더 작성
    writer.writerow(['ID', 'NM'])
    
    # 각 이미지 파일에 대해 행 추가
    for image_file in image_files:
        writer.writerow([image_file, '', ''])

print(f"CSV 파일이 성공적으로 생성되었습니다: {csv_file}")
