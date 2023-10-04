import pandas as pd
import matplotlib.pyplot as plt

import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
# print('current_directory: ', current_directory)
# print('sys.path: ', sys.path)
# myLib_path = os.path.join(current_directory, "myLib")
# sys.path.append(myLib_path)
sys.path.append('../')
# print('sys.path: ', sys.path)
#
# 定义文件名
filename = "D:/github/adamShiau_Python/myAPI/6_v2_readAFI/0928_AFI.txt"

# 使用Pandas读取文本文件，指定以"#"开头的注释行要跳过
data = pd.read_csv(filename, comment='#', delim_whitespace=True, names=["time", "fog", "T", "ax", "ay", "az", "a_T"])

# 打印读取的数据框
print(data['fog'])
