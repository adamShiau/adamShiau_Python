import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# 修改數據處理函數，增加文件來源標識
def process_file(file_path, file_name):
    with open(file_path, 'r') as file:
        file_content = file.read()
    extracted_data = []
    lines = file_content.split("\n")
    for i, line in enumerate(lines):
        timestamp_match = re.match(r"^\d{2}:\d{2}:\d{2} \d{3}$", line.strip())
        if timestamp_match:
            timestamp = timestamp_match.group()
            next_lines = " ".join(lines[i+1:i+6])
            fg_yaw_match = re.search(r"FG_Yaw\[(.*?)\]", next_lines)
            heading_match = re.search(r"Heading\[(.*?)\]", next_lines)
            if fg_yaw_match and heading_match:
                extracted_data.append({
                    "Timestamp": timestamp,
                    "FG_Yaw": fg_yaw_match.group(1),
                    "Heading": heading_match.group(1),
                    "File_Name": file_name
                })
    return pd.DataFrame(extracted_data).drop_duplicates(subset=["Timestamp"])

# 處理資料夾中的所有 .data 檔案
def process_folder(folder_path):
    folder_path = os.path.normpath(folder_path)
    combined_data = pd.DataFrame(columns=["Timestamp", "FG_Yaw", "Heading", "File_Name"])
    for filename in os.listdir(folder_path):
        if filename.endswith(".data"):
            file_path = os.path.join(folder_path, filename)
            combined_data = pd.concat([combined_data, process_file(file_path, filename)], ignore_index=True)
    return combined_data

# 填寫存放 .data 檔案的資料夾路徑
folder_path = r"H:\.shortcut-targets-by-id\1zaas2nfWIlZyL8p7Oyz7ldB9Vl7KrhLl\第二次測試資料\0622"
combined_data = process_folder(folder_path)

# 數據處理
combined_data["Relative_Timestamp"] = pd.to_datetime(combined_data["Timestamp"], format="%H:%M:%S %f")
start_time = combined_data["Relative_Timestamp"].min()
combined_data["Relative_Timestamp"] = (combined_data["Relative_Timestamp"] - start_time).dt.total_seconds()
combined_data["FG_Yaw"] = pd.to_numeric(combined_data["FG_Yaw"], errors='coerce')
combined_data["Heading"] = pd.to_numeric(combined_data["Heading"], errors='coerce')

# 清理和排序數據
combined_data_cleaned = combined_data.dropna().sort_values(by=["File_Name", "Relative_Timestamp"]).reset_index(drop=True)
combined_data_cleaned["Heading_Reversed"] = -combined_data_cleaned["Heading"]

# 調整偏移值，確保起始點對齊
initial_offset = combined_data_cleaned["FG_Yaw"].iloc[0] + combined_data_cleaned["Heading"].iloc[0]
combined_data_cleaned["Heading_Reversed_with_Offset"] = -(combined_data_cleaned["Heading"] - initial_offset)

# 計算誤差訊號
combined_data_cleaned["Error_Signal"] = combined_data_cleaned["FG_Yaw"] - combined_data_cleaned["Heading_Reversed_with_Offset"]

# 設定上下閥值並移除超出範圍的數據
upper_threshold = 1000  # 上閥值
lower_threshold = -1000  # 下閥值
filtered_data = combined_data_cleaned[
    (combined_data_cleaned["Error_Signal"] >= lower_threshold) &
    (combined_data_cleaned["Error_Signal"] <= upper_threshold)
]

# 繪圖函數，添加虛線分隔和設定 Y 軸範圍
def plot_with_separators(data, x_col, y_cols, labels, colors, title, ylim=None):
    plt.figure(figsize=(12, 6))
    files = data["File_Name"].unique()
    for file_name in files:
        file_data = data[data["File_Name"] == file_name]
        for y_col, label, color in zip(y_cols, labels, colors):
            plt.plot(file_data[x_col], file_data[y_col], label=label if file_name == files[0] else "", color=color)
        # 添加虛線分隔
        last_timestamp = file_data[x_col].iloc[-1]
        plt.axvline(x=last_timestamp, color="green", linestyle="--", linewidth=1)
    plt.title(title, fontsize=14)
    plt.xlabel("Relative Timestamp (seconds)", fontsize=12)
    plt.ylabel("Values", fontsize=12)
    plt.legend()
    plt.grid(True)
    # 設置 Y 軸範圍（如果提供）
    if ylim:
        plt.ylim(ylim)

# 第一張圖：FG_Yaw 與 Heading
plot_with_separators(
    filtered_data,
    "Relative_Timestamp",
    ["FG_Yaw", "Heading"],
    ["FG_Yaw", "Heading"],
    ["C0", "C1"],
    "FG_Yaw and Heading vs Relative Timestamp",
    ylim=(-30, 400)
)

# 第二張圖：FG_Yaw 與 Heading_Reversed_with_Offset
plot_with_separators(
    filtered_data,
    "Relative_Timestamp",
    ["FG_Yaw", "Heading_Reversed_with_Offset"],
    ["FG_Yaw", f"Heading Reversed with Offset (Offset={initial_offset:.2f})"],
    ["blue", "red"],
    "FG_Yaw and Heading_Reversed_with_Offset vs Relative Timestamp",
    ylim=(-30, 400)
)

# 第三張圖：誤差訊號
plot_with_separators(
    filtered_data,
    "Relative_Timestamp",
    ["Error_Signal"],
    ["Error Signal (FG_Yaw - Heading_Reversed_with_Offset)"],
    ["purple"],
    "Error Signal vs Relative Timestamp"
    # ylim=(-120, 120)
)

# 顯示所有圖
plt.show()
