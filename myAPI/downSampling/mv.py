import numpy as np
import matplotlib.pyplot as plt

class MovingAverageLPF:
    def __init__(self, window_size):
        self.window_size = window_size
        self.data_buffer = np.zeros(window_size)
        self.pointer = 0

    def filter(self, input_data):
        # 更新環形緩衝區
        self.data_buffer[self.pointer] = input_data
        self.pointer = (self.pointer + 1) % self.window_size

        # 計算移動平均值並返回
        return np.mean(self.data_buffer)

# 測試
if __name__ == "__main__":
    # 參數設置
    datarate = 100000  # 取樣率100 kHz
    cutoff_freq = 60  # 3 dB 頻率為 50 Hz
    window_size = int(datarate / cutoff_freq)

    # 創建一個移動平均濾波器
    lpf = MovingAverageLPF(window_size)

    # 生成一個測試信號
    t = np.linspace(0, 1, datarate)
    # signal = np.sin(2 * np.pi * 50 * t) + np.random.normal(0, 0.5, len(t))
    signal = np.sin(2 * np.pi * 50 * t)

    # 對測試信號進行濾波
    filtered_signal = [lpf.filter(x) for x in signal]

    # 繪製結果
    plt.figure(figsize=(10, 6))
    plt.plot(t, signal, label='Original Signal')
    plt.plot(t, filtered_signal, label='Filtered Signal')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.title('Original vs Filtered Signal')
    plt.legend()
    plt.grid(True)
    plt.show()