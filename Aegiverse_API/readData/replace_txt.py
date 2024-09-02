# 載入所需的函式庫
import os

# 設定檔案名稱
input_filename = '550_0827.txt'  # 原始檔案名稱
output_filename = '550_0827_new.txt'  # 新的輸出檔案名稱

# 初始化變數
variables = []
data = []

# 讀取檔案
with open(input_filename, 'r') as file:
    lines = file.readlines()

    # 過濾掉註釋行
    lines = [line for line in lines if not line.startswith('#')]

    # 獲取變數名稱
    variables = lines[0].strip().split(',')

    # 獲取數據
    for line in lines[1:]:
        data.append(line.strip().split(','))

# 確定要移除的變數的索引
remove_indices = [variables.index('Tx'), variables.index('Ty'), variables.index('Tz')]

# 更新變數和數據
variables = [var for i, var in enumerate(variables) if i not in remove_indices]
data = [[value for i, value in enumerate(row) if i not in remove_indices] for row in data]

# 將修改後的變數和數據寫入新的檔案
with open(output_filename, 'w') as file:
    file.write(','.join(variables) + '\n')
    for row in data:
        file.write(','.join(row) + '\n')

print(f"數據處理完成，已儲存到 '{output_filename}'")
