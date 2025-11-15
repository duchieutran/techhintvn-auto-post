from bs4 import BeautifulSoup
from bs4.element import Comment

def clean_html_advanced(html: str) -> str:
    """
    Tối ưu HTML:
    - Xóa comment HTML
    - Xóa script, style
    - Xóa thuộc tính rác
    - Chuẩn hóa thẻ
    - Loại bỏ div rác, span rác
    """

    if not html or not isinstance(html, str):
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # ============================
    # 1. XÓA COMMENT HTML
    # ============================
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # ============================
    # 2. XÓA SCRIPT + STYLE
    # ============================
    for tag in soup(["script", "style"]):
        tag.decompose()

    # ============================
    # 3. XÓA THUỘC TÍNH RÁC
    # ============================
    remove_attrs = [
        "class", "style", "id", "onclick", "onload",
        "data-*", "aria-*", "role"
    ]

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr in remove_attrs or attr.startswith("data") or attr.startswith("aria"):
                del tag.attrs[attr]

    # ============================
    # 4. XÓA TAG RÁC: <span>, <div> rỗng
    # ============================
    for tag in soup.find_all(["span", "div"]):
        if not tag.text.strip():
            tag.decompose()

    # ============================
    # 5. LÀM ĐẸP LẠI HTML
    # ============================
    cleaned = soup.prettify()

    return cleaned
