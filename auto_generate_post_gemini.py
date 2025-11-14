from google import genai
import os
import random
import datetime
import requests
import json

# ============================
#   CONFIG – API & MODEL
# ============================

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"

BLOGGER_API_KEY = os.environ.get("BLOGGER_API_KEY")
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
- Với mỗi keyword, tạo mô tả meta dài 150–200 ký tự.
- Với mỗi keyword, đánh giá mức độ cạnh tranh: Low, Medium hoặc High.
- Tạo biến {{seo_keywords}} = JSON gồm:
  [
    {{"keyword": "...", "meta": "...", "competition": "..."}},
    ...
  ]

⚠️ TIÊU ĐỀ CHUẨN SEO:
- Không được lặp lại topic.
- 55–70 ký tự.
- Tăng CTR mạnh.
- Tạo biến: {{title_seo}}

⚠️ VIẾT BÀI PHIÊN BẢN {version}/3:
- Viết FULL HTML.
- KHÔNG markdown – KHÔNG ``` – KHÔNG CSS/JS.
- Độ dài mục tiêu: 7000–10000 từ.
- Viết hoàn toàn khác các phiên bản khác (spin content).
- Giữ format YAML.

⚠️ FORMAT XUẤT RA:

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

Sau đó viết bài theo:
- 10–15 mục lớn (h2)
- nhiều mục con (h3)
- bảng <table>
- bullet <ul><li>
- ví dụ thực tế
- FAQ
- kết luận mạnh mẽ

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
            return response.text

        except Exception as e:
            print(f"AI ERROR (attempt {attempt+1}/5): {e}")
            if "overloaded" in str(e).lower():
                print("→ Wait 5s...")
                import time
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
        print(f"=== Tạo phiên bản {v}/3 ===")
        prompt = build_prompt(v)
        html = generate_html(prompt)
        outputs.append((v, html))
    return outputs


# ===============================
#   ĐĂNG LÊN BLOGGER QUA API
# ===============================
def publish_to_blogger(title, content_html):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?key={BLOGGER_API_KEY}"

    data = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html
    }

    response = requests.post(
        url,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        print("🎉 Đăng Blogger thành công!")
        print("URL:", response.json().get("url"))
    else:
        print("❌ Lỗi đăng Blogger:", response.text)



# ===============================
#     CHẠY HỆ THỐNG
# ===============================

versions = generate_all_versions()

for v, html in versions:
    filename = f"posts/post_v{v}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved:", filename)

    # Tự động đăng phiên bản 1 lên Blogger
    if v == 1:
        # lấy title từ YAML dòng 2
        title = html.split("title:")[1].split("\n")[0].replace('"', "").strip()
        publish_to_blogger(title, html)
