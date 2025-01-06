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
            next_lines = " ".join(lines[i + 1:i + 6])
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


# 處理資料夾中的所有 .data 檔案並生成圖表
def process_folder_and_plot_with_index(folder_path, offsets={}):
    folder_path = os.path.normpath(folder_path)
    files = [f for f in os.listdir(folder_path) if f.endswith(".data")]

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        file_data = process_file(file_path, filename)

        # Data processing
        file_data["Relative_Timestamp"] = pd.to_datetime(file_data["Timestamp"], format="%H:%M:%S %f")
        start_time = file_data["Relative_Timestamp"].min()
        file_data["Relative_Timestamp"] = (file_data["Relative_Timestamp"] - start_time).dt.total_seconds()
        file_data["FG_Yaw"] = pd.to_numeric(file_data["FG_Yaw"], errors='coerce')
        file_data["Heading"] = pd.to_numeric(file_data["Heading"], errors='coerce')

        # Clean and calculate relevant columns
        file_data_cleaned = file_data.dropna().sort_values(by=["Relative_Timestamp"]).reset_index(drop=True)
        file_data_cleaned["Heading_Reversed"] = -file_data_cleaned["Heading"]

        # Use provided offset index if available, otherwise default to the first row
        if filename in offsets:
            index = offsets[filename]  # Custom index for offset calculation
            initial_offset = file_data_cleaned["FG_Yaw"].iloc[index] + file_data_cleaned["Heading"].iloc[index]
        else:
            initial_offset = file_data_cleaned["FG_Yaw"].iloc[0] + file_data_cleaned["Heading"].iloc[0]

        file_data_cleaned["Heading_Reversed_with_Offset"] = -(file_data_cleaned["Heading"] - initial_offset)
        file_data_cleaned["Error_Signal"] = file_data_cleaned["FG_Yaw"] - file_data_cleaned[
            "Heading_Reversed_with_Offset"]

        # Generate first plot: FG_Yaw and Heading_Reversed_with_Offset
        plt.figure(figsize=(12, 6))
        plt.plot(file_data_cleaned["Relative_Timestamp"], file_data_cleaned["FG_Yaw"], label="FG_Yaw", color="blue",
                 linestyle='-')
        plt.plot(file_data_cleaned["Relative_Timestamp"], file_data_cleaned["Heading_Reversed_with_Offset"],
                 label="Heading Reversed with Offset", color="red", linestyle='-')
        plt.title(f"FG_Yaw and Heading Reversed with Offset for {filename}", fontsize=14)
        plt.xlabel("Relative Timestamp (seconds)", fontsize=12)
        plt.ylabel("Values", fontsize=12)
        plt.legend()
        plt.grid(True)

        # Generate second plot: Error_Signal
        plt.figure(figsize=(12, 6))
        plt.plot(file_data_cleaned["Relative_Timestamp"], file_data_cleaned["Error_Signal"],
                 label="Error Signal", color="purple", linestyle='-')
        plt.title(f"Error Signal for {filename}", fontsize=14)
        plt.xlabel("Relative Timestamp (seconds)", fontsize=12)
        plt.ylabel("Error", fontsize=12)
        plt.legend()
        plt.grid(True)

    # Show all figures at once
    plt.show()


# 設定資料夾路徑
folder_path = r"H:\.shortcut-targets-by-id\1zaas2nfWIlZyL8p7Oyz7ldB9Vl7KrhLl\第二次測試資料\0622"  # 替換為資料夾路徑

# 輸入偏移索引（可選）
custom_offsets = {
    "2024-06-22-10-13-18.data": 500  # 對應第 5 筆數據
}

# 處理資料夾並生成圖表
process_folder_and_plot_with_index(folder_path, custom_offsets)
