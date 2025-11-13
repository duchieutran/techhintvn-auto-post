import os
import json
import base64
import yaml
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = os.getenv("BLOG_ID")

def upload_post(filename, creds):
    with open(filename, "r", encoding="utf-8") as f:
        raw = f.read()

    # Parse metadata (YAML)
    front, body = raw.split("---", 2)[1:]
    meta = yaml.safe_load(front)

    title = meta.get("title", "No Title")
    labels = meta.get("labels", [])

    service = build("blogger", "v3", credentials=creds)

    post = {
        "kind": "blogger#post",
        "title": title,
        "content": body,
        "labels": labels
    }

    service.posts().insert(blogId=BLOG_ID, body=post).execute()
    print(f"Đã đăng: {title}")

def main():
    creds = Credentials.from_authorized_user_info(json.loads(os.getenv("TOKEN_JSON")))
    posts = sorted(os.listdir("posts"))

    if not posts:
        print("Không có bài nào để đăng.")
        return

    first = posts[0]
    filepath = os.path.join("posts", first)

    upload_post(filepath, creds)

    # Xóa bài đã đăng
    os.remove(filepath)
    print(f"Đã xóa file: {first}")

if __name__ == "__main__":
    main()
