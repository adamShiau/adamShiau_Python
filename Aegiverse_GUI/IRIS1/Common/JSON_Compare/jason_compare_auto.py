import serial
import json
import time
from datetime import datetime

# 設定序列埠參數
SERIAL_PORT = "COM19"   # 修改成你的Port，例如 /dev/ttyUSB0
BAUDRATE = 115200      # 修改成你的Baudrate
TIMEOUT = 1            # 讀取 timeout 秒數

# HEX 指令清單
commands = [
    "AB BA 66 00 00 00 02 01 55 56",
    "AB BA 66 00 00 00 02 02 55 56",
    "AB BA 66 00 00 00 02 03 55 56",
    "AB BA 81 00 00 00 02 01 55 56"
]

def hexstr_to_bytes(hex_str):
    """將字串形式的 HEX 轉成 bytes"""
    return bytes.fromhex(hex_str)

def dump_parameters():
    """發送指令並收集 JSON，存成檔案，檔名帶時間戳"""
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT)
    time.sleep(2)  # 等待設備準備好

    # 建立新檔名，例如 para_20250822_103012.txt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"para_{timestamp}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        for cmd in commands:
            ser.write(hexstr_to_bytes(cmd))
            line = ser.readline().decode("utf-8").strip()
            if line:
                try:
                    json.loads(line)  # 確認是合法 JSON
                    f.write(line + "\n")
                    print(f"[OK] 收到 JSON: {line}")
                except json.JSONDecodeError:
                    print(f"[WARN] 收到非 JSON: {line}")
            time.sleep(0.1)  # 10 ms 間隔

    ser.close()
    print(f"[INFO] 已儲存檔案: {output_file}")
    return output_file

def load_params(file_path):
    """讀取 txt，每行是一個 JSON，回傳 list of dict"""
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def compare_params(file1, file2):
    """比較兩個 JSON 檔案內容差異"""
    params1 = load_params(file1)
    params2 = load_params(file2)

    max_len = max(len(params1), len(params2))
    for i in range(max_len):
        if i >= len(params1):
            print(f"Line {i+1}: only in {file2}")
            continue
        if i >= len(params2):
            print(f"Line {i+1}: only in {file1}")
            continue

        dict1, dict2 = params1[i], params2[i]
        diffs = []
        for key in set(dict1.keys()).union(dict2.keys()):
            v1 = dict1.get(key)
            v2 = dict2.get(key)
            if v1 != v2:
                diffs.append((key, v1, v2))

        if diffs:
            print(f"Line {i+1} differences:")
            for key, v1, v2 in diffs:
                print(f"  key {key}: {file1}={v1}, {file2}={v2}")
        else:
            print(f"Line {i+1}: identical")

if __name__ == "__main__":
    # 1️⃣ 每次執行都 dump 新檔案
    new_file = dump_parameters()

    # 2️⃣ 永遠和 para0.txt 比較
    compare_params("para0.txt", new_file)
