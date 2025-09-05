import matplotlib.pyplot as plt
import pandas as pd


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

    # 嘗試將數據轉換為數值類型
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 無法轉換的數據填充 NaN

    return df.dropna()  # 移除包含 NaN 的行，確保繪圖時不出錯


# 檔案名稱
filename = "IRIS_02-27.txt"

df = read_iris_file(filename)

# 繪製 time 數據
plt.figure(figsize=(10, 5))
plt.plot(df['time'], marker='o', linestyle='-')
plt.xlabel("Index")
plt.ylabel("Time")
plt.title("Time Plot from IRIS_02-27.txt")
plt.grid()
plt.show()
