import os
import json
import yaml
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = os.environ["BLOG_ID"]

creds = json.loads(os.environ["TOKEN_JSON"])

credentials = Credentials(
    creds["token"],
    refresh_token=creds["refresh_token"],
    token_uri=creds["token_uri"],
    client_id=creds["client_id"],
    client_secret=creds["client_secret"],
    scopes=["https://www.googleapis.com/auth/blogger"]
)

service = build("blogger", "v3", credentials=credentials)

# lấy bài mới nhất
files = sorted(os.listdir("posts"), reverse=True)
file_path = "posts/" + files[0]

print("Reading:", file_path)

with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

# tách YAML
parts = data.split("---")
if len(parts) < 3:
    raise Exception("❌ YAML ERROR: Không thể tách YAML. Kiểm tra format bài viết!")

yaml_raw = parts[1]
html_body = "---".join(parts[2:])

meta = yaml.safe_load(yaml_raw)

post = {
    "kind": "blogger#post",
    "title": meta["title"],
    "labels": meta["labels"],
    "content": html_body,
}

res = service.posts().insert(
    blogId=BLOG_ID,
    body=post,
    isDraft=False
).execute()

print("POSTED:", res["url"])
