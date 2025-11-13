import google.generativeai as genai
import yaml
import os
import random
import datetime
import base64

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Model PRO
MODEL = "gemini-1.5-pro"

# Chủ đề thông minh
TOPICS = [
    "AI Tools hữu ích cho sinh viên",
    "Thủ thuật Android / iPhone 2025",
    "Fix lỗi Windows / phần mềm",
    "Kỹ năng học tập / Productivity",
    "Tối ưu điện thoại cho sinh viên",
    "AI hỗ trợ học tập & nghiên cứu",
]

topic = random.choice(TOPICS)

def generate_thumbnail(prompt_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    img = model.generate_image(prompt=f"Tạo ảnh minh họa dạng poster đơn giản, chủ đề: {prompt_text}")
    output_path = f"posts/thumb_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    with open(output_path, "wb") as f:
        f.write(img.image)

    return output_path

def generate_article():
    prompt = f"""
Bạn là AI Writer chuyên viết blog SEO 2025.

❗ Hãy viết bài thật dài **10.000 từ**, chia nội dung thành nhiều phần:
- Mở bài
- 10–15 mục lớn (h2)
- Các mục con (h3)
- Bullet points
- Danh sách
- Box note
- FAQ
- Kết luận đặc biệt chuẩn SEO

❗ Xuất đúng định dạng:
- YAML ở đầu
- Nội dung 100% HTML
- Tuyệt đối KHÔNG Markdown ở phần nội dung

❗ YAML phải như sau:
---
title: "Bài viết chủ đề: {topic}"
labels: AUTO_LABEL
description: "Mô tả chuẩn SEO cho bài viết {topic}"
status: "publish"
thumbnail: AUTO_THUMB
---

❗ AUTO_LABEL: AI phải tự chọn 1 trong 4:
- ai-tools
- tech-tips
- study-skill
- fix-errors

❗ AUTO_THUMB: đường dẫn file ảnh thumbnail đã tạo

❗ Bài viết phải ~10.000 từ.
❗ Ngôn ngữ: Tiếng Việt.
❗ Văn phong: rõ ràng – hấp dẫn – đúng SEO – dễ đọc.

Hãy bắt đầu viết bài ngay.
"""

    model = genai.GenerativeModel(MODEL)
    result = model.generate_content(prompt)
    return result.text

# Tạo folder
os.makedirs("posts", exist_ok=True)

# Tạo thumbnail
thumb_path = generate_thumbnail(topic)

# Tạo bài
raw_content = generate_article()

# Thay thế AUTO_THUMB
raw_content = raw_content.replace("AUTO_THUMB", thumb_path)

# Thay thế AUTO_LABEL
if "AI" in topic or "AI Tools" in topic:
    label = "ai-tools"
elif "Android" in topic or "iPhone" in topic:
    label = "tech-tips"
elif "kỹ năng" in topic or "Productivity" in topic:
    label = "study-skill"
else:
    label = "fix-errors"

raw_content = raw_content.replace("AUTO_LABEL", f'["{label}"]')

# Lưu file
filename = f"posts/post_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(raw_content)

print("Generated:", filename)
