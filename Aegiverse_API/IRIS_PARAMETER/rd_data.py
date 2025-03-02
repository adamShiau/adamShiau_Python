import matplotlib.pyplot as plt
import pandas as pd

# 讀取檔案，忽略 # 開頭的註釋行
def read_iris_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) == 3:
                    try:
                        time = float(parts[0])  # 轉換為浮點數
                        fog = float(parts[1])
                        temp = float(parts[2])
                        data.append([time, fog, temp])
                    except ValueError:
                        continue  # 若有無法轉換的數據則跳過
    return pd.DataFrame(data, columns=['time', 'fog', 'T'])

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
