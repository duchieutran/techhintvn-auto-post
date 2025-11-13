import os
import json
import yaml
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ===============================
#  ĐỌC TOKEN + BLOG ID
# ===============================
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


# ===============================
#  LẤY FILE MỚI NHẤT
# ===============================

if not os.path.exists("posts"):
    raise Exception("❌ Thư mục 'posts/' không tồn tại!")

files = [f for f in os.listdir("posts") if f.endswith(".html")]
files = sorted(files, reverse=True)

if len(files) == 0:
    raise Exception("❌ Không tìm thấy file HTML nào trong thư mục posts/!")

file_path = "posts/" + files[0]
print("Reading:", file_path)

with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

# ===============================
#  TÁCH YAML
# ===============================
parts = data.split("---")

if len(parts) < 3:
    raise Exception("❌ YAML ERROR: Không thể tách YAML. Kiểm tra format bài viết!")

yaml_raw = parts[1].strip()
html_body = "---".join(parts[2:]).strip()

# parse YAML
try:
    meta = yaml.safe_load(yaml_raw)
except Exception as e:
    raise Exception("❌ YAML không hợp lệ!\n" + str(e))

# kiểm tra trường bắt buộc
required_fields = ["title", "labels", "description", "status"]

for field in required_fields:
    if field not in meta:
        raise Exception(f"❌ YAML thiếu trường bắt buộc: {field}")

print("YAML OK — Title:", meta["title"])
print("Labels:", meta["labels"])

# ===============================
#  GỬI LÊN BLOGGER
# ===============================

post_data = {
    "kind": "blogger#post",
    "title": meta["title"],
    "labels": meta["labels"],
    "content": html_body
}

print("📡 Đang đăng bài lên Blogger...")

res = service.posts().insert(
    blogId=BLOG_ID,
    body=post_data,
    isDraft=False
).execute()

print("🎉 ĐÃ ĐĂNG THÀNH CÔNG!")
print("URL:", res.get("url", "Không rõ URL"))


# ===============================
#  XOÁ FILE SAU KHI ĐĂNG (TUỲ CHỌN)
# ===============================

DELETE_AFTER_POST = True

if DELETE_AFTER_POST:
    try:
        os.remove(file_path)
        print("🗑 Đã xoá file:", file_path)
    except Exception as e:
        print("⚠ Không xoá được file:", e)
