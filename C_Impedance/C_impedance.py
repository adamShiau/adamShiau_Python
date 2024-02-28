import numpy as np
import matplotlib.pyplot as plt

# 定義方程
def impedance(w, R, L, C):
    return np.sqrt(R**2 + (w*L)**2 * (1 - 1/(w**2 * L * C))**2)

# 設定參數
R = 500e-3
L = 5e-9
C = 10e-6

# 產生頻率範圍
w_values = np.logspace(0, 10, 10000)

# 計算對應的阻抗值
z_values = impedance(w_values, R, L, C)

# 繪製圖形
plt.figure(figsize=(10, 6))
plt.loglog(w_values, z_values, label='Impedance')
plt.title('Impedance vs Frequency')
plt.xlabel('Frequency (w)')
plt.ylabel('Impedance (z)')
plt.grid(True)
plt.legend()
plt.show()