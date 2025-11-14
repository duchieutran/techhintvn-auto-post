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
#   CSS BEAUTIFY (TỰ CHÈN)
# ===============================

BEAUTIFY_CSS = """
<style>

  /* ==========================
       FONT + BODY
  ========================== */
  body, p {
    font-size: 18px;
    line-height: 1.8;
    color: #222;
    font-family: "Inter", "Roboto", Arial, sans-serif;
    margin: 0;
    padding: 0;
  }

  /* ==========================
       HEADING STYLE
  ========================== */
  h1, h2, h3 {
    letter-spacing: 0.3px;
    word-spacing: 2px;
    line-height: 1.35;
  }

  h1 {
    font-size: 34px;
    margin: 25px 0 15px;
    font-weight: 800;
    color: #111;
    border-left: 6px solid #4A90E2;
    padding-left: 12px;
    animation: fadeIn 0.6s ease-in-out;
  }

  h2 {
    font-size: 28px;
    font-weight: 700;
    margin-top: 45px;
    margin-bottom: 15px;
    color: #222;
    position: relative;
  }

  h2:hover {
    color: #0d6efd;
    transition: 0.15s ease;
  }

  h3 {
    font-size: 23px;
    margin-top: 30px;
    margin-bottom: 10px;
    font-weight: 600;
  }

  /* ==========================
       PARAGRAPH EFFECT
  ========================== */
  p {
    margin: 14px 0;
  }

  p:hover {
    background: #fafafa;
    transition: 0.2s ease;
    padding-left: 4px;
  }

  /* ==========================
       UL + LI BEAUTIFY
  ========================== */
  ul {
    margin: 15px 0 20px 25px;
    padding: 0;
  }

  ul li {
    margin-bottom: 10px;
    line-height: 1.7;
    list-style: none;
    position: relative;
    padding-left: 24px;
  }

  ul li:before {
    content: "✔";
    position: absolute;
    left: 0;
    top: 2px;
    color: #4CAF50;
    font-weight: bold;
  }

  /* ==========================
       TABLE STYLE
  ========================== */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 16px;
  }

  table th {
    background: #f0f4ff;
    font-weight: 700;
    border-bottom: 2px solid #d0d7ff;
  }

  table td, table th {
    padding: 12px 14px;
    border: 1px solid #ddd;
  }

  table tr:hover {
    background: #f5f8ff;
    transition: 0.15s;
  }

  /* ==========================
       BLOCKQUOTE
  ========================== */
  blockquote {
    border-left: 4px solid #00a8ff;
    padding-left: 15px;
    margin: 20px 0;
    background: #f8fbff;
    color: #555;
    font-style: italic;
    animation: fadeIn 0.5s ease;
  }

  /* ==========================
        IMAGE STYLE
  ========================== */
  img {
    max-width: 100%;
    border-radius: 8px;
    margin: 18px 0;
    transition: transform 0.25s ease;
  }

  img:hover {
    transform: scale(1.02);
  }

  /* ==========================
        LINK + HOVER
  ========================== */
  a {
    color: #0066cc;
    text-decoration: none;
    font-weight: 600;
  }

  a:hover {
    text-decoration: underline;
    color: #004aad;
  }

  /* ==========================
        HIGHLIGHT BOX
  ========================== */
  .note-box {
    background: #e8f4ff;
    border-left: 5px solid #2196F3;
    padding: 15px;
    margin: 18px 0;
    border-radius: 4px;
  }

  .warning-box {
    background: #fff5e6;
    border-left: 5px solid #ff9800;
    padding: 15px;
    margin: 18px 0;
    border-radius: 4px;
  }

  /* ==========================
        CODE BLOCK BEAUTIFY
  ========================== */
  pre {
    background: #1e1e1e;
    padding: 14px;
    border-radius: 6px;
    color: #eee;
    overflow-x: auto;
    margin: 20px 0;
  }

  code {
    color: #ffdd57;
    font-size: 15px;
  }

  /* ==========================
        SIMPLE FADE ANIMATION
  ========================== */
  @keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }

</style>
"""



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

{BEAUTIFY_CSS}

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

            return response.text or ""

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
        "Authorization": f"Bearer {ACCESS_TOKEN}",
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

    filename = f"posts/post_v{v}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("📁 Saved:", filename)

    if v == 1:
        try:
            title = html.split("title:")[1].split("\n")[0].replace('"', "").strip()
            publish_to_blogger(title, html)
        except Exception as e:
            print("❌ Lỗi lấy title:", e)
