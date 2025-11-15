# auto_internal_linker.py
import requests
import xml.etree.ElementTree as ET
import re


BLOG_URL = "https://techhintvn.blogspot.com"   # sửa nếu khác


# ================================
# 1) LẤY TOÀN BỘ LINK TỪ SITEMAP
# ================================
def get_all_posts():
    urls = []
    page = 1

    while True:
        sitemap_url = f"{BLOG_URL}/sitemap.xml?page={page}"
        r = requests.get(sitemap_url)

        if r.status_code != 200:
            break

        root = ET.fromstring(r.text)

        for url in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(url.text)

        page += 1

    return list(set(urls))  # loại trùng lặp


# ================================
# 2) TÌM BÀI VIẾT LIÊN QUAN
# ================================
def clean_text(s):
    return re.sub(r"[^a-zA-Z0-9áàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ ]", " ", s.lower())

def similarity(a, b):
    a_words = set(clean_text(a).split())
    b_words = set(clean_text(b).split())
    if not a_words or not b_words:
        return 0
    return len(a_words & b_words) / len(a_words | b_words)


def find_related_posts(new_title, all_urls):
    related = []

    for link in all_urls:
        title = link.rsplit("/", 1)[-1].replace(".html", "")
        score = similarity(new_title, title)
        related.append((score, link))

    related.sort(reverse=True)
    top_links = [x[1] for x in related[:5]]
    return top_links


# ================================
# 3) CHÈN INTERNAL LINK VÀO BÀI MỚI
# ================================
def insert_internal_links(html, links):
    if not links:
        return html

    box = "<h2>Bài viết liên quan</h2><ul>"
    for l in links:
        box += f'<li><a href="{l}">{l}</a></li>'
    box += "</ul>"

    # Chèn sau thẻ <h1>
    return html.replace("</h1>", "</h1>" + box)


# ================================
# 4) API CHÍNH (được gọi trong tool chính)
# ================================
def auto_add_internal_links(title, html):
    print("🔍 Đang tải danh sách bài viết từ sitemap...")
    posts = get_all_posts()

    print(f"📌 Tổng bài đã tìm được: {len(posts)}")

    print("🔍 Đang tìm bài liên quan...")
    links = find_related_posts(title, posts)

    print("🔗 Chèn Internal Links...")
    return insert_internal_links(html, links)
