import os
import json
from Bio import Entrez
import requests
from bs4 import BeautifulSoup, Doctype, NavigableString
import re
import time

# PubMed API 사용 설정
Entrez.email = "hb0522@snu.ac.kr"
LAST_INDEX_FILE = "last_index.json"
STRUCTURED_DATA_FILE = "structured_data.json"
IMAGE_URLS_FILE = "image_urls.json"
RETRY_LIMIT = 5  # 최대 재시도 횟수
WAIT_TIME = 10  # 재시도 전 대기 시간 (초)
BATCH_SIZE = 1000  # 한 번에 가져올 최대 결과 수

def fetch_article_details(pubmed_id):
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            return records
        except Exception as e:
            print(f"Error fetching details for PubMed ID {pubmed_id}: {e}")
            retries += 1
            if retries < RETRY_LIMIT:
                print(f"Retrying in {WAIT_TIME} seconds...")
                time.sleep(WAIT_TIME)
    return None

def extract_doi_from_details(article_details):
    for article in article_details.get('PubmedArticle', []):
        article_ids = article['PubmedData']['ArticleIdList']
        for id in article_ids:
            if id.attributes.get('IdType') == 'doi':
                return id
    return None

def extract_title_from_details(article_details):
    for article in article_details.get('PubmedArticle', []):
        title = article['MedlineCitation']['Article'].get('ArticleTitle')
        if title:
            return title
    return "Title not found"

def extract_abstract_from_details(article_details):
    for article in article_details.get('PubmedArticle', []):
        abstract = article['MedlineCitation']['Article'].get('Abstract')
        if abstract:
            return " ".join([str(ab) for ab in abstract['AbstractText']])
    return "Abstract not found"

def extract_html_from_pubmed(pubmed_id):
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching HTML for PubMed ID {pubmed_id}: {e}")
            retries += 1
            if retries < RETRY_LIMIT:
                print(f"Retrying in {WAIT_TIME} seconds...")
                time.sleep(WAIT_TIME)
    return None

def get_full_text_html(doi):
    url = f"https://doi.org/{doi}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries >= RETRY_LIMIT:
                break
            else:
                time.sleep(WAIT_TIME)
        except Exception as e:
            break
    return None

def recursive_find_images_and_captions(tag, image_links, figure_captions, figure_labels):
    if isinstance(tag, (Doctype, NavigableString)):
        return
    
    if tag.name == 'figure':
        img_tag = tag.find('img')
        figcaption_tag = tag.find('figcaption')

        if img_tag and figcaption_tag:
            src = img_tag.get('data-src')
            if not src:
                src = img_tag.get('src')
            caption_text = figcaption_tag.get_text(strip=True)
            if src and caption_text:
                image_links.append(src)
                figure_captions.append(caption_text)
                match = re.match(r'^(FIGURE \d+|Figure \d+|Fig\.? \d+|IMAGE \d+|Image \d+|Img\.? \d+|Plate \d+)[.:]?', caption_text, re.IGNORECASE)
                if match:
                    label = match.group(0).rstrip('.:')
                    figure_labels.append(label)

    if list(tag.children):
        for child in tag.children:
            recursive_find_images_and_captions(child, image_links, figure_captions, figure_labels)

def parse_html_for_information(html, is_pubmed=True):
    soup = BeautifulSoup(html, 'html.parser')
    
    if is_pubmed:
        title = soup.find('h1', class_='heading-title').get_text(strip=True) if soup.find('h1', class_='heading-title') else "Title not found"
        abstract_div = soup.find('div', class_='abstract-content')
        abstract = abstract_div.get_text(strip=True) if abstract_div else "Abstract not found"
    else:
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Title not found"
        abstract_div = soup.find('div', class_='abstract-content')
        abstract = abstract_div.get_text(strip=True) if abstract_div else "Abstract not found"
    
    global image_links, figure_captions

    image_links = []
    figure_captions = []
    figure_labels = []
    recursive_find_images_and_captions(soup, image_links, figure_captions, figure_labels)
    
    paragraphs = []
    for label in figure_labels:
        label_pattern = re.compile(re.escape(label), re.IGNORECASE)
        for p in soup.find_all('p'):
            if label_pattern.search(p.get_text(strip=True)):
                paragraphs.append(p.get_text(strip=True))
    
    return {
        "title": title,
        "abstract": abstract,
        "image_links": image_links,
        "figure_captions": figure_captions,
        "figure_labels": figure_labels,
        "paragraphs": paragraphs
    }

def structure_information(data):
    structured_data = []
    for link, caption in zip(data['image_links'], data['figure_captions']):
        description = ' '.join(data['paragraphs'])
        structured_data.append({
            "Title": data['title'],
            "Abstract": data['abstract'],
            "Url": link,
            "Caption": caption,
            "Description": description
        })
    return structured_data

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def append_to_json(new_data, filename):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    data.extend(new_data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def save_last_index(last_index, filename='last_index.json'):
    with open(filename, 'w') as f:
        json.dump({"last_index": last_index}, f)

def load_last_index(filename='last_index.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            last_index = json.load(f).get("last_index", 0)
            print(f"Loaded last index: {last_index}")
            return last_index
    return 0

def process_data_in_batches(query, max_results, batch_size=10, end_index=None):
    start_index = load_last_index()
    print(f"Start index: {start_index}")
    total_ids = []

    # ids.txt 파일에서 논문 ID 읽기
    with open("/home/hb0522/MLLM/MLLM1/ids.txt", "r") as f:
        ids = f.read().splitlines()
        total_ids.extend(ids)
    print(f"Total number of IDs fetched: {len(total_ids)}")

    if end_index is None:
        end_index = len(total_ids)

    structured_data_list = []
    image_urls_list = []

    for start_idx in range(start_index, min(end_index, len(total_ids)), batch_size):
        end_idx = min(start_idx + batch_size, end_index)
        batch_ids = total_ids[start_idx:end_idx]
        
        print(f"Processing batch: {start_idx}-{end_idx}")

        for pubmed_id in batch_ids:
            article_details = fetch_article_details(pubmed_id)
            if not article_details:
                continue  # article_details를 가져오지 못하면 다음 논문으로 넘어감

            title = extract_title_from_details(article_details)
            abstract = extract_abstract_from_details(article_details)
            # print(f"Title: {title}")

            doi = extract_doi_from_details(article_details)
            # print(f"DOI: {doi}")
            
            if doi:
                full_text_html = get_full_text_html(doi)
                if full_text_html:
                    parsed_data = parse_html_for_information(full_text_html, is_pubmed=False)
                    if parsed_data and parsed_data['image_links']:  # 이미지 URL이 있는 경우만 처리
                        print(parsed_data)
                        parsed_data['abstract'] = abstract  # Abstract 추가
                        structured_data = structure_information(parsed_data)
                        structured_data_list.extend(structured_data)
                        print(structured_data)
                        image_urls_list.extend(parsed_data['image_links'])
                        print(parsed_data['image_links'])
                    else:
                        # pass
                        print(f"Skipping article with DOI: {doi} due to image access restrictions.")
                else:
                    print(f"Skipping article with DOI: {doi} due to access restrictions.")
                    # pass
            else:
                # pass
                print(f"DOI not found for PubMed ID: {pubmed_id}")
        
        # 마지막으로 처리한 인덱스 저장
        save_last_index(end_idx)  # 시작 인덱스 + 배치 크기로 업데이트
        
        # 추출한 데이터 저장
        append_to_json(structured_data_list, STRUCTURED_DATA_FILE)
        append_to_json(image_urls_list, IMAGE_URLS_FILE)
        
        # 데이터 초기화
        structured_data_list = []
        image_urls_list = []

        # 일정 시간 대기
        time.sleep(5)  # 5초 대기 (필요에 따라 조정 가능)
    
    return structured_data_list

# "Bone Scan"에 대한 논문 검색 및 처리
query = "Cardiac Perfusion Scan"
max_results = 100000
batch_size = 10

# 특정 인덱스까지만 처리하도록 end_index 파라미터 추가
end_index = 36999  # 원하는 인덱스 값으로 설정

structured_data_list = process_data_in_batches(query, max_results, batch_size, end_index)

# 추출한 데이터 출력
for data in structured_data_list:
    print(data)
