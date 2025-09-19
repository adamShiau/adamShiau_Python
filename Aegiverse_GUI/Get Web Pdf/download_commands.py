import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin

# --- Commands 各分類入口 ---
COMMANDS_SECTIONS = {
    "3DM (0x0C)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x0c/0x0c_links.htm",
    "Aiding (0x13)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x13/0x13_links.htm",
    "Base (0x01)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x01/0x01_links.htm",
    "Filter (0x0D)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x0d/0x0d_links.htm",
    "GNSS (0x0E)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x0e/0x0e_links.htm",
    "System (0x7F)": "https://s3.us-east-1.amazonaws.com/files.microstrain.com/CV7_GNSS_INS_Online/external_content/dcp/Commands/0x7f/0x7f_links.htm"
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
    """收集某一分類（例如 3DM）的所有子頁"""
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
for name, url in COMMANDS_SECTIONS.items():
    print(f"📥 收集 {name} ...")
    pages = collect_pages(url)
    print(f"  -> 找到 {len(pages)} 個頁面")

    output_file = f"MIP_API_Commands_{name.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}.pdf"
    print(f"📄 產生 PDF: {output_file}")

    pdfkit.from_url(pages, output_file, configuration=config, options=options)

print("🎉 Commands 分類 PDF 全部生成完成！")
