import os
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image

HEADERS = {"User-Agent": "Mozilla/5.0"}

def is_valid_url(url):
    if url is None:
        return False

    bad_keywords = ["logo", "icon", "default", "blank", "github"]
    return not any(word in url.lower() for word in bad_keywords)



def is_valid_image(path):
    try:
        with Image.open(path) as img:
            width, height = img.size

            # too small
            if width < 100 or height < 150:
                return False

            ratio = width / height

            if ratio > 1.2:   
                return False

        return True
    except:
        return False


def get_image_url(page_url):
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        tag = soup.find("meta", property="og:image")
        if tag:
            return tag["content"]

        img_tag = soup.find("img", id="coverImage")
        if img_tag:
            return img_tag.get("src")

    except Exception as e:
        return None


def download_image(img_url, save_path):
    try:
        response = requests.get(img_url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except:
        pass

    return False


def scrape_images(df, save_dir="images"):
    os.makedirs(save_dir, exist_ok=True)

    success = 0
    failed = 0

    for i, (_, row) in enumerate(df.iterrows()):
        url = row["url"]
        book_id = row["id"]

        filepath = os.path.join(save_dir, f"{book_id}.jpg")

        if os.path.exists(filepath):
            continue

        for attempt in range(3):
            img_url = get_image_url(url)

            if img_url and is_valid_url(img_url):
                if download_image(img_url, filepath):

                    # validate image
                    if is_valid_image(filepath):
                        success += 1
                        break
                    else:
                        os.remove(filepath)

            time.sleep(1)

        else:
            failed += 1
            print(f"[FAILED] {url}")

        if i % 50 == 0:
            print(f"Processed: {i} | Success: {success} | Failed: {failed}")

        time.sleep(1)

    print(f"\nDone! Success: {success}, Failed: {failed}")