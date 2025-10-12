import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin
from pypdf import PdfReader, PdfWriter

# ==============================
# 🧩 控制選項
# ==============================
GENERATE_SINGLE_PDFS = True    # 是否生成每一分類獨立 PDF
MERGE_ALL_IN_ONE     = True    # 是否將所有分類合併成一份
DELETE_TEMP_PDFS     = True    # 合併後是否刪除中間檔

BOOKMARK_ROOT_NAME = "Data Overview"
SAVE_PATH = "manual/MIP Protocol"
SAVE_NAME = "Data_Overview.pdf"

# ==============================
# 📂 輸出資料夾
# ==============================
# OUTPUT_DIR = os.path.join(os.getcwd(), SAVE_PATH, BOOKMARK_ROOT_NAME)
OUTPUT_DIR = os.path.join(os.getcwd(), SAVE_PATH)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# 1️⃣ Commands 各分類入口
# ==============================
COMMANDS_SECTIONS = {
    "Data Overview": "https://s3.amazonaws.com/files.microstrain.com/CV7_INS_Manual/dcp_content/introduction/Data%20Overview.htm",
    "MIP Continuation Packets": "https://s3.amazonaws.com/files.microstrain.com/CV7_INS_Manual/dcp_content/introduction/MIP%20Continuation%20Packets.htm",
    "Shared Data Descriptors": "https://s3.amazonaws.com/files.microstrain.com/CV7_INS_Manual/dcp_content/introduction/Shared%20Data%20Descriptors.htm"
}

# ==============================
# 2️⃣ 手動補充遺漏頁
# ==============================
EXTRA_PAGES = {

}

# ==============================
# 3️⃣ wkhtmltopdf 設定
# ==============================
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
options = {
    'enable-javascript': '',
    'javascript-delay': 4000,
    'no-stop-slow-scripts': '',
    'enable-local-file-access': '',
    'encoding': "UTF-8"
}

# ==============================
# 4️⃣ 抓取子頁面
# ==============================
def collect_pages(entry_url):
    """收集子頁面（含 0x / 非 0x 項目）"""
    ordered_urls = [entry_url]
    try:
        resp = requests.get(entry_url)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠️ 無法開啟 {entry_url}: {e}")
        return ordered_urls

    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select("a[href]"):
        href = a["href"].strip()
        full_url = urljoin(entry_url, href)

        if (
            href.startswith("#")
            or "Home" in href
            or "Product" in href
            or not href.lower().endswith(".htm")
            or "CV7_INS_Manual" not in full_url
        ):
            continue

        if full_url not in ordered_urls:
            ordered_urls.append(full_url)

    return ordered_urls


# ==============================
# 5️⃣ 逐一下載 PDF
# ==============================
generated_pdfs = []

if GENERATE_SINGLE_PDFS:
    for name, url in COMMANDS_SECTIONS.items():
        print(f"\n📥 收集 {name} ...")
        pages = collect_pages(url)

        if name in EXTRA_PAGES:
            print(f"➕ 加入 {len(EXTRA_PAGES[name])} 個手動補頁")
            pages.extend(EXTRA_PAGES[name])

        print(f"📑 共找到 {len(pages)} 個頁面")

        output_file = os.path.join(OUTPUT_DIR, f"MIP_API_Commands_{name.replace(' ', '_').replace('(', '').replace(')', '')}.pdf")
        print(f"📄 產生 PDF: {output_file}")
        pdfkit.from_url(pages, output_file, configuration=config, options=options)
        generated_pdfs.append(output_file)

# ==============================
# 6️⃣ 合併成單一 PDF
# ==============================
if MERGE_ALL_IN_ONE and generated_pdfs:
    print("\n📚 開始合併所有分類 PDF ...")

    writer = PdfWriter()
    outline_root = writer.add_outline_item(BOOKMARK_ROOT_NAME, 0)
    current_page = 0

    for pdf_path in generated_pdfs:
        print(f"➡️ 合併 {pdf_path} ...")
        reader = PdfReader(pdf_path)

        section_title = os.path.basename(pdf_path).replace("MIP_API_Commands_", "").replace(".pdf", "")
        section_outline = writer.add_outline_item(section_title, current_page, parent=outline_root)

        # 加入頁面
        for page in reader.pages:
            writer.add_page(page)

        # 匯入書籤
        try:
            def import_outline(items, parent=None, base_page=current_page):
                for it in items:
                    if isinstance(it, list):
                        import_outline(it, parent, base_page)
                        continue

                    title = None
                    if isinstance(it, dict):
                        title = it.get("Title") or it.get("/Title")
                        page_idx = it.get("Page") or it.get("/Page") or 0
                    elif hasattr(it, "title"):
                        title = getattr(it, "title", None)
                        try:
                            page_idx = reader.get_destination_page_number(it)
                        except Exception:
                            page_idx = 0
                    elif hasattr(it, "get"):
                        title = it.get("/Title")
                        page_idx = it.get("/Page", 0)
                    else:
                        title = str(it)
                        page_idx = 0

                    if not title or title.strip() == "":
                        title = "Untitled"

                    try:
                        writer.add_outline_item(title, base_page + int(page_idx), parent=parent)
                    except Exception:
                        writer.add_outline_item(title, base_page, parent=parent)

            if reader.outline:
                import_outline(reader.outline, section_outline, current_page)
        except Exception as e:
            print(f"⚠️ 匯入書籤時發生問題：{e}")

        current_page += len(reader.pages)

    final_pdf = os.path.join(OUTPUT_DIR, SAVE_NAME)
    with open(final_pdf, "wb") as f_out:
        writer.write(f_out)

    print(f"🎯 已成功產生合併後的 PDF：{final_pdf}")

    # 清理中間檔
    if DELETE_TEMP_PDFS and GENERATE_SINGLE_PDFS:
        for f in generated_pdfs:
            try:
                os.remove(f)
                print(f"🧹 已刪除暫存檔：{f}")
            except Exception:
                pass
