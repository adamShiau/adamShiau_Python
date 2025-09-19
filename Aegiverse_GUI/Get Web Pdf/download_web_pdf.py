import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin

# --- Filter 章節首頁 ---
FILTER_URL = "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Data/0x82/0x82_links.htm"
OUTPUT_PDF = "MIP_API_Filter.pdf"

# wkhtmltopdf 路徑（請改成你安裝的實際路徑）
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# --- PDF 轉換選項 ---
options = {
    'enable-javascript': '',
    'javascript-delay': 3000,   # 等 3 秒確保內容載入
    'no-stop-slow-scripts': '', # 避免腳本過早終止
    'enable-local-file-access': '',  # 允許存取外部資源
    'encoding': "UTF-8"
}

# --- 收集頁面 ---
ordered_page_urls = [FILTER_URL]  # 先加首頁

# 下載並解析首頁，找出子頁
resp = requests.get(FILTER_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

for a in soup.select("a"):
    href = a.get("href")
    text = a.text.strip()
    if href and ("0x" in text or "Uncertainty" in text or "Bias" in text):
        full_url = urljoin(FILTER_URL, href)
        ordered_page_urls.append(full_url)

print(f"✅ 收集到 {len(ordered_page_urls)} 個頁面")
for u in ordered_page_urls:
    print(" -", u)

# --- 產生 PDF ---
pdfkit.from_url(ordered_page_urls, OUTPUT_PDF, configuration=config, options=options)

print("🎉 PDF 完成:", OUTPUT_PDF)
