import matplotlib.pyplot as plt
import pandas as pd
import os


# 讀取檔案，忽略 # 開頭的註釋行
def read_iris_file(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]

    # 第一行為標題行
    header = lines[0].split(',')
    data = [line.split(',') for line in lines[1:]]

    # 確保所有行的列數與標題一致
    data = [row for row in data if len(row) == len(header)]

    # 轉換數據類型
    df = pd.DataFrame(data, columns=header)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 無法轉換的數據填充 NaN

    return df.dropna()  # 移除包含 NaN 的行


# 刪除 overflow 後的數據
def remove_overflow_data(df):
    if 'time' not in df.columns:
        raise ValueError("資料中不包含 'time' 欄位")

    # 找到第一個 time 為負數的索引
    overflow_index = df[df['time'] < 0].index.min()

    # 如果存在 overflow，則刪除之後的數據
    if not pd.isna(overflow_index):
        df = df.loc[:overflow_index - 1]

    return df


# 處理檔案
def process_file(filename):
    df = read_iris_file(filename)
    df_fixed = remove_overflow_data(df)

    # 產生新檔名
    base, ext = os.path.splitext(filename)
    new_filename = f"{base}-fix{ext}"
    df_fixed.to_csv(new_filename, index=False)
    print(f"處理完成，已儲存為 {new_filename}")

    # 繪製修正後的 time 數據
    plt.figure(figsize=(10, 5))
    plt.plot(df_fixed['time'], marker='o', linestyle='-')
    plt.xlabel("Index")
    plt.ylabel("Time")
    plt.title(f"Time Plot from {new_filename}")
    plt.grid()
    plt.show()


# 執行處理
filename = "IRIS_02-27.txt"
process_file(filename)
