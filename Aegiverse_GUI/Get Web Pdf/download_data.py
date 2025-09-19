import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin

# --- Data 區塊分類入口 ---
DATA_SECTIONS = {
    "Filter (0x82)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x82/0x82_links.htm",
    "GNSS Recv 1 (0x91)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x91/0x91_links.htm",
    "GNSS Recv 2 (0x92)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x92/0x92_links.htm",
    "GNSS Corrections (0x93)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x93/0x93_links.htm",
    "GNSS External (0x94)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x94/0x94_links.htm",
    "System (0xA0)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0xa0/0xa0_links.htm",
    "Shared (0xFF)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0xff/0xff_links.htm",
    "Sensor (0x80)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x80/0x80_links.htm"
}

# wkhtmltopdf 路徑（請改成你的實際安裝位置）
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# PDF 轉換選項
options = {
    'enable-javascript': '',
    'javascript-delay': 4000,   # 多等一點，避免空白
    'no-stop-slow-scripts': '',
    'enable-local-file-access': '',
    'encoding': "UTF-8"
}

def collect_pages(entry_url):
    """收集某一分類（例如 Filter）的所有子頁"""
    ordered_urls = [entry_url]
    resp = requests.get(entry_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select("a"):
        href = a.get("href")
        text = a.text.strip()
        if href and ("0x" in text or "Uncertainty" in text or "Bias" in text):
            full_url = urljoin(entry_url, href)
            ordered_urls.append(full_url)

    return ordered_urls

# --- 逐一下載每個分類 ---
for name, url in DATA_SECTIONS.items():
    print(f"📥 收集 {name} ...")
    pages = collect_pages(url)
    print(f"  -> 找到 {len(pages)} 個頁面")

    output_file = f"MIP_API_{name.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}.pdf"
    print(f"📄 產生 PDF: {output_file}")

    pdfkit.from_url(pages, output_file, configuration=config, options=options)

print("🎉 全部分類 PDF 生成完成！")
