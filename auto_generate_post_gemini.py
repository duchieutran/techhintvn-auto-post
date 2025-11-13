from google import genai
import os
import random
import datetime

# Tạo client với API key từ GitHub Secrets
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# MODEL mới chuẩn AI Google 2025
MODEL = "gemini-2.5-flash"

TOPICS = [
    "AI Tools hữu ích cho sinh viên",
    "Thủ thuật Android / iPhone 2025",
    "Fix lỗi Windows / phần mềm",
    "Kỹ năng học tập / Productivity",
    "Tối ưu điện thoại cho sinh viên",
    "AI hỗ trợ học tập & nghiên cứu",
]

topic = random.choice(TOPICS)

# tạo folder posts/
os.makedirs("posts", exist_ok=True)


# ===============================
#      TẠO LABEL TỰ ĐỘNG
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
#     TẠO BÀI 10.000 TỪ
# ===============================
def generate_article_html():
    prompt = f"""
Bạn là AI Writer chuyên viết blog SEO.

Viết bài cực dài ~10.000 từ.
Nội dung thuần HTML, KHÔNG markdown, KHÔNG ```.

Bắt buộc xuất ra đúng format:

---
title: "Bài viết chủ đề: {topic}"
labels: ["{label}"]
description: "Mô tả chuẩn SEO cho {topic}"
status: "publish"
thumbnail: ""
---

<h1>Bài viết chủ đề: {topic}</h1>

<p>Đoạn mở bài...</p>

Sau đó viết thật dài theo cấu trúc:
- 10–15 mục lớn (h2)
- nhiều mục con (h3)
- bullet points (<ul><li>)
- FAQ
- kết luận

KHÔNG được dùng markdown.
KHÔNG được tự ý thay đổi format YAML.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return response.text


# tạo bài viết
html = generate_article_html()

# lưu file
filename = f"posts/post_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(html)

print("Generated:", filename)
