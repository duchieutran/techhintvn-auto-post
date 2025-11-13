import openai
import json
from datetime import datetime

# Nhận KEY từ GitHub Secrets
API_KEY = json.loads(open("../../token_ai.json"))["api_key"]
openai.api_key = API_KEY

def generate_post():
    prompt = """
Bạn là TechHintVN AI Writer.
Viết bài thật dài (tối đa token), chuẩn SEO, 100% ở dạng MARKDOWN + HTML.

FORMAT bắt buộc:

---
title: "{TIÊU_ĐỀ_CHUẨN_SEO}"
labels: ["{label}"]
description: "{MÔ_TẢ_120_KÝ_TỰ}"
status: "publish"
---

<h1>{TIÊU_ĐỀ_CHUẨN_SEO}</h1>

{NỘI_DUNG_HTML_RẤT_DÀI}

Yêu cầu:
- Chủ đề blog: AI Tools, thủ thuật công nghệ, productivity sinh viên, fix lỗi Windows.
- Nội dung phải rất dài (max token ChatGPT cho phép).
- Dùng thẻ <h2>, <h3>, <p>, <ul>, <li>, <pre>.
- Dùng giọng văn chuyên nghiệp + dễ đọc.
- Tự chọn 1 chủ đề phù hợp và viết bài hoàn chỉnh.
"""

    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia viết blog SEO."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=6500,
        temperature=0.8,
    )

    article = response.choices[0].message["content"]

    filename = "generated_post.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)

    return filename


if __name__ == "__main__":
    print("Generating article...")
    file = generate_post()
    print(f"Created: {file}")
