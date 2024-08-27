import os
import json
import requests
from tqdm import tqdm
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/17.17134",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"
]

def download_image(url, referer, save_path, max_retries=7):
    if url.startswith('//'):
        url = 'https:' + url

    for attempt in range(max_retries):
        user_agent = random.choice(user_agents)
        headers = {
            "User-Agent": user_agent,
            "Referer": referer,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cookie": "your_cookie_here"
        }

        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code in [403, 404]:
                # print(f"Skipping URL {url}: HTTP {response.status_code}")
                return None
            response.raise_for_status()
            with open(save_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)
            # print(f"Downloaded and saved image from {url} to {save_path}")
            return save_path
        except requests.RequestException as e:
            # print(f"Attempt {attempt + 1} failed for URL {url} with error: {e}")
            continue
    return None

def download_and_save_image(item, image_dir, referer="https://www.springernature.com"):
    image_url = item.get("Url")
    if image_url:
        image_id = item["ID"]
        save_path = os.path.join(image_dir, f"{image_id}.jpg")
        downloaded_path = download_image(image_url, referer, save_path)
        if downloaded_path:
            item["ImagePath"] = downloaded_path
        else:
            item["ImagePath"] = None
    return item

def process_json_file(input_filename, image_dir, start_index=0):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 지정된 인덱스부터 시작
    data = data[start_index:]

    for item in tqdm(data, desc="Downloading images", initial=start_index, total=len(data) + start_index):
        try:
            download_and_save_image(item, image_dir)
        except Exception as e:
            print(f"An error occurred: {e}")

# 변수 설정
input_filename = '/home/hb0522/MLLM/MLLM1/cleaned_data.json'
image_dir = '/home/hb0522/MLLM/MLLM1/downloaded_images'
start_index = 0 

# 디렉토리 생성
os.makedirs(image_dir, exist_ok=True)

# JSON 파일 처리
process_json_file(input_filename, image_dir, start_index)
