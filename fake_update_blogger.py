# fake_update_blogger.py
import requests
import xml.etree.ElementTree as ET
import random
import json
import os

BLOG_URL = "https://techhintvn.blogspot.com"
ACCESS_TOKEN = os.environ.get("BLOGGER_ACCESS_TOKEN")
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")


# ====== Lấy danh sách bài từ Sitemap ======
def get_all_posts():
    urls = []
    page = 1

    while True:
        url = f"{BLOG_URL}/sitemap.xml?page={page}"
        r = requests.get(url)
        if r.status_code != 200:
            break

        xml = ET.fromstring(r.text)

        for loc in xml.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(loc.text)

        page += 1

    return urls


# ====== Lấy postId từ URL ======
def extract_post_id(url):
    # Blogger API dùng ID dạng số rất dài (fetch từ API)
    api = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/bypath?path={url}"

    r = requests.get(api, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})

    if r.status_code == 200:
        return r.json().get("id")
    return None


# ====== Cập nhật bài viết mà không đổi nội dung ======
def fake_update(post_id):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    
    r = requests.get(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    if r.status_code != 200:
        return False

    post_data = r.json()

    # Không đổi nội dung, chỉ PUT lại để Blogger cập nhật thời gian
    update = requests.put(
        url,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"},
        data=json.dumps(post_data),
    )

    return update.status_code == 200


# ====== MAIN ======
def run_fake_update():
    posts = get_all_posts()
    if not posts:
        print("❌ Không tìm được bài nào!")
        return

    random_post = random.choice(posts)
    print("🔄 Fake update bài:", random_post)

    post_id = extract_post_id(random_post)
    if not post_id:
        print("❌ Không lấy được postId")
        return

    if fake_update(post_id):
        print("🎉 Fake update thành công!")
    else:
        print("❌ Fake update thất bại!")


if __name__ == "__main__":
    run_fake_update()
