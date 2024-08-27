import os
import json
import aiohttp
import asyncio
from tqdm.asyncio import tqdm_asyncio
import openai
import random
from openai import OpenAI

# OpenAI API 키 설정
# client = OpenAI(
#     api_key=
# )

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

async def download_image(session, url, referer, save_path, max_retries=7):
    # URL이 스킴을 포함하지 않는 경우 추가
    if url.startswith('//'):
        url = 'https:' + url

    for attempt in range(max_retries):
        for user_agent in user_agents:
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
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status in [403, 404]:
                        return None
                    response.raise_for_status()
                    with open(save_path, 'wb') as out_file:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            out_file.write(chunk)
                    return save_path
            except (aiohttp.ClientError, asyncio.TimeoutError):
                await asyncio.sleep(random.uniform(0.5, 1.5))
    return None

async def create_combined_description(item):
    prompt = f"""
    Title: {item['Title']}
    Abstract: {item['Abstract']}
    Caption: {item['Caption']}
    Description: {item['Description']}

    Based on the information above, create a coherent and concise description for the image, explaining its significance and context in 1-3 paragraphs. Please use almost all information related to the image. Always refer to the uploaded image as 'This image' and do not use expressions like 'Figure 1' or any other figure numbers. If the uploaded image is consisted of several sub-figures and remarked as A, B or other alphabets and there are information for each of them, please (you must) explain them respectively. If there is no respective description, explain image as one single image.
    """

    try:
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

        combined_description = response.choices[0].message.content.strip()
        return {"ID": item["ID"], "Description": combined_description}

    except Exception as e:
        print(f"Error generating description for ID {item['ID']}: {e}")
        return {"ID": item["ID"], "Description": "Error generating description"}

async def download_and_save_image(session, item, image_dir, referer="https://www.springernature.com"):
    image_url = item.get("Url")
    if image_url:
        image_id = item["ID"]
        save_path = os.path.join(image_dir, f"{image_id}.jpg")
        downloaded_path = await download_image(session, image_url, referer, save_path)
        if downloaded_path:
            item["ImagePath"] = downloaded_path
        else:
            item["ImagePath"] = None
    return item

async def process_json_file(input_filename, output_filename, image_dir):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    combined_descriptions = []

    async with aiohttp.ClientSession() as session:
        tasks = [download_and_save_image(session, item, image_dir) for item in data]
        for task in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Downloading images"):
            result = await task
            if result["ImagePath"] is not None:
                description_result = await create_combined_description(result)
                combined_descriptions.append(description_result)

            # 파일 업데이트
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(combined_descriptions, f, indent=4)

# 변수 설정
input_filename = '/home/hb0522/MLLM/MLLM1/JSONs/cleaned_data_LungScan_filtered.json'
output_filename = '/home/hb0522/MLLM/MLLM1/JSONs/Descriptions_LungScan_filtered.json'
image_dir = '/home/hb0522/MLLM/MLLM1/Data/downloaded_images3'

# 디렉토리 생성
os.makedirs(image_dir, exist_ok=True)

# JSON 파일 처리
asyncio.run(process_json_file(input_filename, output_filename, image_dir))
