# ===============================
#   CLEAN HTML NÂNG CAO – FULL
# ===============================

import re
import html
from bs4 import BeautifulSoup

def clean_html_advanced(raw_html):
    # ===============================
    # 1. Giải mã entity cơ bản
    # ===============================
    raw_html = html.unescape(raw_html)

    # ===============================
    # 2. XÓA KÝ TỰ ZERO-WIDTH
    # ===============================
    zero_width = r"[\u200B-\u200F\uFEFF]"
    raw_html = re.sub(zero_width, "", raw_html)

    # ===============================
    # 3. XÓA CÁC ENTITY SAI
    # ===============================
    raw_html = re.sub(r"&#x?[0-9A-Fa-f]{2,6};", "", raw_html)
    raw_html = re.sub(r"&#\d{2,6};", "", raw_html)

    # ===============================
    # 4. XÓA EMOJI – Unicode > U+FFFF
    # ===============================
    raw_html = re.sub(r"[\U00010000-\U0010FFFF]", "", raw_html)

    # ===============================
    # 5. XÓA KÝ TỰ CONTROL
    # ===============================
    raw_html = re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", "", raw_html)

    # ===============================
    # 6. CHUẨN HÓA DẤU & và khoảng trắng
    # ===============================
    raw_html = raw_html.replace("&nbsp;", " ")
    raw_html = raw_html.replace("&amp;", "&")
    raw_html = re.sub(r"\s+", " ", raw_html)

    # ===============================
    # 7. BEAUTY HTML – LOẠI BỎ TAG RÁC
    # ===============================
    soup = BeautifulSoup(raw_html, "html.parser")

    # Xoá span vô dụng
    for span in soup.find_all("span"):
        if not span.attrs:
            span.unwrap()
        else:
            # Nếu span chỉ có style màu → bỏ màu
            if "style" in span.attrs:
                del span["style"]
            # Nếu rỗng → xóa
            if not span.text.strip():
                span.decompose()

    # Xoá div rác rỗng
    for div in soup.find_all("div"):
        if not div.text.strip() and not div.find("img"):
            div.decompose()

    # Xoá tag comment
    for comment in soup(text=lambda text: isinstance(text, (BeautifulSoup.Comment))):
        comment.extract()

    # ===============================
    # 8. Loại bỏ script/style (Blogger chặn)
    # ===============================
    for tag in soup(["script", "style"]):
        tag.decompose()

    # ===============================
    # 9. Loại bỏ inline style nguy hiểm
    # ===============================
    for tag in soup.find_all(True):
        if "style" in tag.attrs:
            del tag["style"]

    # ===============================
    # 10. Format lại HTML đẹp
    # ===============================
    cleaned_html = soup.prettify()

    # ===============================
    # 11. Xoá khoảng trắng đầu/cuối
    # ===============================
    cleaned_html = cleaned_html.strip()

    return cleaned_html
