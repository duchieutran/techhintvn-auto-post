import json
import os
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

with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

# tách YAML
raw = data.split("---")
yaml_raw = raw[1]
html_body = "---".join(raw[2:])

import yaml
meta = yaml.safe_load(yaml_raw)

post = {
    "kind": "blogger#post",
    "title": meta["title"],
    "labels": meta["labels"],
    "content": html_body
}

res = service.posts().insert(blogId=BLOG_ID, body=post, isDraft=False).execute()

print("POSTED:", res["url"])
