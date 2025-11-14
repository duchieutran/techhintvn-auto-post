from google import genai
import os
import random
import datetime
import requests
import json
import time


# ============================
#   CONFIG – API & MODEL
# ============================

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"

ACCESS_TOKEN = os.environ.get("BLOGGER_ACCESS_TOKEN")   # 🔥 DÙNG OAUTH TOKEN
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")

TOPICS = [
    "AI Tools hữu ích cho sinh viên",
    "Thủ thuật Android / iPhone 2025",
    "Fix lỗi Windows / phần mềm",
    "Kỹ năng học tập / Productivity",
    "Tối ưu điện thoại cho sinh viên",
    "AI hỗ trợ học tập & nghiên cứu",
]

topic = random.choice(TOPICS)

os.makedirs("posts", exist_ok=True)


# ===============================
#   LABEL TỰ ĐỘNG
# ===============================
def auto_label(t):
    t = t.lower()
    if "ai" in t:
        return "ai-tools"
    if "android" in t or "iphone" in t:
        return "tech-tips"
    if "kỹ năng" in t or "productivity" in t:
        return "study-skill"
    return "fix-errors"


label = auto_label(topic)


# ===============================
#    PROMPT CHÍNH TẠO 1 BÀI
# ===============================
def build_prompt(version):
    return f"""
Bạn là AI Writer chuyên viết blog SEO.

⚠️ TẠO 5 KEYWORD + PHÂN TÍCH
- Hãy tạo danh sách 5 keyword SEO liên quan tới "{topic}".
- Với mỗi keyword, tạo meta description dài 150–200 ký tự.
- Với mỗi keyword, đánh giá cạnh tranh: Low, Medium hoặc High.
- Tạo biến JSON {{seo_keywords}}.

⚠️ TIÊU ĐỀ CHUẨN SEO:
- KHÔNG được giống hệt topic.
- Dài 55–70 ký tự.
- Tăng CTR mạnh.
- Tạo biến {{title_seo}}.

⚠️ VIẾT BÀI PHIÊN BẢN {version}/3:
- FULL HTML.
- KHÔNG markdown, KHÔNG ``` , KHÔNG CSS/JS.
- Độ dài: 7000–10000 từ.
- SPIN hoàn toàn so với các phiên bản khác.
- Giữ đúng format YAML.

📌 FORMAT XUẤT:

---
title: "{{title_seo}}"
labels: ["{label}"]
description: "Mô tả chuẩn SEO cho chủ đề {topic}"
keywords: "{{seo_keywords}}"
status: "publish"
thumbnail: ""
version: "{version}"
---

<h1>{{title_seo}}</h1>

<p>Đoạn mở bài dài và hấp dẫn...</p>

⚠️ Sau đó viết bài theo:
- 10–15 mục lớn (h2)
- nhiều mục con (h3)
- bảng <table>
- bullet <ul><li>
- ví dụ thực tế
- FAQ
- kết luận mạnh

KHÔNG dùng markdown.
"""


# ===============================
#    GỌI GEMINI – TẠO 1 BÀI
# ===============================
def generate_html(prompt):
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )

            return response.text or ""   # 🔥 chặn lỗi None

        except Exception as e:
            print(f"⚠️ AI ERROR (attempt {attempt+1}/5): {e}")

            if "overloaded" in str(e).lower() or "unavailable" in str(e).lower():
                print("→ Model quá tải, chờ 5 giây...")
                time.sleep(5)
            else:
                raise e

    raise Exception("❌ Model overloaded quá nhiều lần!")


# ===============================
#     TẠO 3 PHIÊN BẢN (SPIN)
# ===============================
def generate_all_versions():
    outputs = []
    for v in range(1, 4):
        print(f"\n=== Tạo phiên bản {v}/3 ===")
        prompt = build_prompt(v)
        html = generate_html(prompt)
        outputs.append((v, html))
    return outputs


# ===============================
#   ĐĂNG LÊN BLOGGER (OAUTH)
# ===============================
def publish_to_blogger(title, content_html):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",    # 🔥 DÙNG TOKEN
    }

    data = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("\n🎉 Đăng Blogger thành công!")
        print("URL:", response.json().get("url"))
    else:
        print("\n❌ Lỗi đăng Blogger:", response.text)


# ===============================
#     CHẠY HỆ THỐNG
# ===============================

versions = generate_all_versions()

for v, html in versions:

    if not html.strip():
        print(f"❌ Phiên bản {v} bị rỗng! Bỏ qua.")
        continue

    # lưu file
    filename = f"posts/post_v{v}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("📁 Saved:", filename)

    # Tự động đăng phiên bản 1
    if v == 1:
        try:
            # lấy title từ YAML
            title = html.split("title:")[1].split("\n")[0].replace('"', "").strip()
            publish_to_blogger(title, html)
        except Exception as e:
            print("❌ Lỗi lấy title:", e)
