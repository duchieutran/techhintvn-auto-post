from google import genai
from clean_html_advanced import clean_html_advanced
import os
import random
import datetime
import requests
import json
import time

# ==========================================
#   CONFIG – API & MODEL
# ==========================================
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-pro"

ACCESS_TOKEN = os.environ.get("BLOGGER_ACCESS_TOKEN")
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

# ==========================================
#   LABEL AUTO
# ==========================================
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

# ==========================================
#   CSS CỦA BÀI VIẾT
# ==========================================
BEAUTIFY_CSS = """<style>body,p{font-size:18px;line-height:1.8;color:#222;font-family:Inter,Roboto,Arial,sans-serif}h1,h2,h3{line-height:1.35}h1{font-size:34px;margin:25px 0 15px;font-weight:800;color:#111;border-left:6px solid #4A90E2;padding-left:12px}h2{font-size:28px;font-weight:700;margin-top:45px;margin-bottom:15px}h3{font-size:23px;margin-top:30px;margin-bottom:10px;font-weight:600}p{margin:14px 0}ul{margin:15px 0 20px 25px;padding:0}ul li{margin-bottom:10px;line-height:1.7;list-style:none;position:relative;padding-left:24px}ul li:before{content:"✔";position:absolute;left:0;top:2px;color:#4CAF50;font-weight:bold}table{width:100%;border-collapse:collapse;margin:25px 0;font-size:16px}table th{background:#f0f4ff;font-weight:700;border-bottom:2px solid #d0d7ff}table td,table th{padding:12px 14px;border:1px solid #ddd}blockquote{border-left:4px solid #00a8ff;padding-left:15px;margin:20px 0;background:#f8fbff;color:#555;font-style:italic}img{max-width:100%;border-radius:8px;margin:18px 0}</style>"""

# ==========================================
#   BUILD PROMPT TẠO 1 BÀI
# ==========================================
def build_prompt(version):
    return f"""
Bạn là AI Writer chuyên viết blog SEO.

⚠️ HÃY TẠO 5 KEYWORD CHUẨN SEO:
- Tạo danh sách 5 keyword liên quan đến "{topic}".
- Với mỗi keyword → tạo meta description 150–200 ký tự.
- Đánh giá mức cạnh tranh: Low / Medium / High.
- Tạo biến JSON {{seo_keywords}}.

⚠️ TẠO TITLE CHUẨN SEO:
- KHÔNG được giống topic.
- Dài 55–70 ký tự.
- Tăng CTR mạnh.
- Biến: {{title_seo}}.

⚠️ VIẾT BÀI PHIÊN BẢN {version}/3:
- FULL HTML (KHÔNG markdown).
- KHÔNG dùng ký tự ```.
- Độ dài yêu cầu: 7000–10000 từ.
- Unique hoàn toàn so với các phiên bản khác.

📌 FORMAT BẮT BUỘC:

---
title: "{{title_seo}}"
labels: ["{label}"]
description: "Mô tả chuẩn SEO cho chủ đề {topic}"
keywords: "{{seo_keywords}}"
status: "publish"
thumbnail: ""
version: "{version}"
---

{BEAUTIFY_CSS}

<h1>{{title_seo}}</h1>
<p>Đoạn mở bài hấp dẫn...</p>

⚠️ SAU ĐÓ VIẾT:
- 10–15 mục lớn (h2)
- nhiều mục con (h3)
- bảng <table>
- bullet <ul><li>
- ví dụ thực tế
- FAQ
- kết luận mạnh

KHÔNG markdown.
KHÔNG ký tự code block.
"""


# ==========================================
#   GỌI GEMINI – SINH NỘI DUNG
# ==========================================
def generate_html(prompt):
    wait_times = [5, 10, 20, 40, 60, 80, 120, 150, 180, 200]  # retry 10 lần

    for attempt in range(len(wait_times)):
        try:
            response = client.models.generate_content(
                model="gemini-pro",   # model ổn định hơn flash
                contents=prompt,
            )

            return clean_html_advanced(response.text or "")

        except Exception as e:
            print(f"⚠️ AI ERROR attempt {attempt+1}/{len(wait_times)} → {e}")

            if ("overloaded" in str(e).lower()
                or "unavailable" in str(e).lower()
                or "503" in str(e)):
                sleep_time = wait_times[attempt]
                print(f"→ Model quá tải, chờ {sleep_time}s rồi thử lại...")
                time.sleep(sleep_time)
                continue
            else:
                raise e

    raise Exception("❌ Model quá tải quá nhiều lần (đã thử 10 lần)!")



# ==========================================
#   TẠO 3 PHIÊN BẢN
# ==========================================
def generate_all_versions():
    outputs = []
    for v in range(1, 4):
        print(f"\n=== Đang tạo phiên bản {v}/3 ===")
        html = generate_html(build_prompt(v))
        outputs.append((v, html))
    return outputs


# ==========================================
#   ĐĂNG LÊN BLOGGER
# ==========================================
def publish_to_blogger(title, html_content):
    html_content = clean_html_advanced(html_content)

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    data = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("🎉 Đăng Blogger thành công!")
        print("URL:", response.json().get("url"))
    else:
        print("❌ Blogger Error:", response.text)


# ==========================================
#   MAIN SYSTEM – TẠO + LƯU + ĐĂNG
# ==========================================
versions = generate_all_versions()

for v, html in versions:

    filename = f"posts/post_v{v}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("📁 Saved:", filename)

    if v == 1:
        try:
            # lấy title trong YAML
            title_line = html.split("title:")[1].split("\n")[0]
            title = title_line.replace('"', "").replace("'", "").strip()
            publish_to_blogger(title, html)

        except Exception as e:
            print("❌ Lỗi lấy title:", e)
