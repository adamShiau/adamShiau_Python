import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# 讀取並處理單個檔案
def process_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    extracted_data = []
    lines = file_content.split("\n")
    for i, line in enumerate(lines):
        timestamp_match = re.match(r"^\d{2}:\d{2}:\d{2} \d{3}$", line.strip())
        if timestamp_match:
            timestamp = timestamp_match.group()
            next_lines = " ".join(lines[i+1:i+6])  # Combine next lines for FG_Yaw and Heading
            fg_yaw_match = re.search(r"FG_Yaw\[(.*?)\]", next_lines)
            heading_match = re.search(r"Heading\[(.*?)\]", next_lines)
            if fg_yaw_match and heading_match:
                extracted_data.append({
                    "Timestamp": timestamp,
                    "FG_Yaw": fg_yaw_match.group(1),
                    "Heading": heading_match.group(1)
                })
    # 轉換為 DataFrame 並刪除重複數據
    return pd.DataFrame(extracted_data).drop_duplicates(subset=["Timestamp"])

# 從資料夾中讀取所有 .data 檔案
def process_folder(folder_path):
    combined_data = pd.DataFrame(columns=["Timestamp", "FG_Yaw", "Heading"])
    for filename in os.listdir(folder_path):
        if filename.endswith(".data"):
            file_path = os.path.join(folder_path, filename)
            combined_data = pd.concat([combined_data, process_file(file_path)], ignore_index=True)
    return combined_data

# 填寫存放 .data 檔案的資料夾路徑
folder_path = r"H:\.shortcut-targets-by-id\1zaas2nfWIlZyL8p7Oyz7ldB9Vl7KrhLl\第二次測試資料\0622"
combined_data = process_folder(folder_path)

# 確保數據為數字類型並計算相對時間戳
combined_data["Relative_Timestamp"] = pd.to_datetime(combined_data["Timestamp"], format="%H:%M:%S %f")
start_time = combined_data["Relative_Timestamp"].min()
combined_data["Relative_Timestamp"] = (combined_data["Relative_Timestamp"] - start_time).dt.total_seconds()
combined_data["FG_Yaw"] = pd.to_numeric(combined_data["FG_Yaw"], errors='coerce')
combined_data["Heading"] = pd.to_numeric(combined_data["Heading"], errors='coerce')
combined_data_cleaned = combined_data.dropna()

# 繪製圖形
plt.figure(figsize=(12, 6))
plt.plot(combined_data_cleaned["Relative_Timestamp"], combined_data_cleaned["FG_Yaw"], label="FG_Yaw", color="blue", linestyle='-')
plt.plot(combined_data_cleaned["Relative_Timestamp"], combined_data_cleaned["Heading"], label="Heading", color="red", linestyle='-')
plt.title("FG_Yaw and Heading vs Relative Timestamp", fontsize=14)
plt.xlabel("Relative Timestamp (seconds)", fontsize=12)
plt.ylabel("Values", fontsize=12)
plt.legend()
plt.grid(True)
plt.show()
