import os
from Bio import Entrez
import time
import json

# PubMed API 사용 설정
Entrez.email = "hb0522@snu.ac.kr"
RETRY_LIMIT = 5  # 최대 재시도 횟수
WAIT_TIME = 10  # 재시도 전 대기 시간 (초)
BATCH_SIZE = 1000  # 한 번에 가져올 최대 결과 수
MAX_RESULTS_PER_BATCH = 9999  # 한 번에 가져올 최대 결과 수 제한

LAST_INDEX_FILE = "last_index.json"

def save_last_index(last_index, filename=LAST_INDEX_FILE):
    with open(filename, 'w') as f:
        json.dump({"last_index": last_index}, f)

def load_last_index(filename=LAST_INDEX_FILE):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            last_index = json.load(f).get("last_index", 0)
            print(f"Loaded last index: {last_index}")
            return last_index
    return 0

def search_pubmed(query, retstart, retmax, mindate, maxdate):
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retstart=retstart, retmax=retmax, mindate=mindate, maxdate=maxdate)
            record = Entrez.read(handle)
            handle.close()
            return record['IdList']
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            retries += 1
            if retries < RETRY_LIMIT:
                print(f"Retrying in {WAIT_TIME} seconds...")
                time.sleep(WAIT_TIME)
            else:
                print("Max retries exceeded. Stopping.")
                break
    return []

def save_ids_to_file(ids, filename):
    with open(filename, 'w') as f:
        for pubmed_id in ids:
            f.write(pubmed_id + '\n')

def process_data_in_batches(query, start_year, end_year, max_results_per_year=9999):
    total_ids = []

    for year in range(start_year, end_year + 1):
        start_index = load_last_index()
        for batch_start in range(start_index, max_results_per_year, BATCH_SIZE):
            ids = search_pubmed(query, retstart=batch_start, retmax=BATCH_SIZE, mindate=f"{year}/01/01", maxdate=f"{year}/12/31")
            total_ids.extend(ids)
            print(f"Fetched {len(ids)} IDs starting at {batch_start} for year {year}")

            # 중간 결과를 저장
            save_last_index(batch_start + len(ids))

            # 검색 결과가 더 이상 없으면 종료
            if len(ids) < BATCH_SIZE:
                break

            # 일정 시간 대기
            time.sleep(1)  # 너무 빠른 요청을 피하기 위해 대기

        # 연도별로 완료된 후 인덱스 초기화
        save_last_index(0)

    return total_ids

# 검색 쿼리와 최대 검색 결과 수 설정
query = "Cardiac Perfusion Scan"
start_year = 1950
end_year = 2024
output_file = "ids.txt"

# 논문 ID 검색 및 파일 저장
ids = process_data_in_batches(query, start_year, end_year)
save_ids_to_file(ids, output_file)

print(f"총 {len(ids)}개의 논문 ID가 {output_file} 파일에 저장되었습니다.")
