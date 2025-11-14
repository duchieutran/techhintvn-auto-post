from google import genai
import os
import random
import datetime

# Tạo client từ GitHub Secrets
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# MODEL chuẩn AI Google 2025
MODEL = "gemini-2.5-flash"

# Chủ đề ngẫu nhiên
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

⚠️ QUY ĐỊNH TIÊU ĐỀ:
- KHÔNG được đặt tiêu đề giống topic: "{topic}".
- Hãy tự tạo một tiêu đề SEO thật HẤP DẪN, dài 60–70 ký tự, tăng CTR.
- Tiêu đề phải chứa từ khóa chính nhưng KHÔNG được trùng exact topic.
- Tạo biến {{title_seo}} = tiêu đề SEO cuối cùng.

⚠️ QUY ĐỊNH NỘI DUNG:
- Viết bài cực dài ~10.000 từ.
- Nội dung thuần HTML, KHÔNG markdown, KHÔNG ```.
- KHÔNG được tự ý thay đổi format YAML.
- KHÔNG được chèn CSS hoặc JavaScript.

Xuất ra đúng format:

---
title: "{{title_seo}}"
labels: ["{label}"]
description: "Mô tả chuẩn SEO cho chủ đề {topic}"
status: "publish"
thumbnail: ""
---

<h1>{{title_seo}}</h1>

<p>Đoạn mở bài dài và hấp dẫn...</p>

Sau đó viết thật dài theo cấu trúc:

- 10–15 mục lớn (h2)
- Nhiều mục con (h3)
- Bullet points (<ul><li>)
- Thêm bảng nếu phù hợp (<table>)
- Nhiều ví dụ thực tế
- FAQ dài
- Kết luận mạnh mẽ

KHÔNG dùng markdown.
KHÔNG lặp lại topic trong tiêu đề.
KHÔNG được thay đổi YAML.
    """

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text

        except Exception as e:
            print(f"AI ERROR (attempt {attempt+1}/5):", e)

            if any(x in str(e).lower() for x in ["overloaded", "unavailable", "rate limit"]):
                print("→ Model quá tải, tạm chờ 5 giây...")
                import time
                time.sleep(5)
                continue
            else:
                raise e

    raise Exception("❌ AI FAILED: Model overloaded quá nhiều lần!")


# tạo bài viết
html = generate_article_html()

# Tạo tên file
filename = f"posts/post_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

# lưu file
with open(filename, "w", encoding="utf-8") as f:
    f.write(html)

print("Generated:", filename)
