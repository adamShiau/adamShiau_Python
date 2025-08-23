#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

import serial

# ================== 使用者可調整參數 ==================
FPGA_PORT = "COM12"         # 儀器上電時會從這裡輸出 fpga_para
MCU_PORT  = "COM3"          # MCU 會從這裡輸出 mcu_para (4 行 JSON)
BAUDRATE  = 115200          # 若不同請調整
READ_SILENCE_SEC = 5.0      # 連續這麼久沒有任何資料就視為結束
GLOBAL_TIMEOUT_SEC = 30.0   # 最長等待秒數（避免無限等）
SAVE_DIR = Path(".")        # 檔案儲存資料夾
# =====================================================

# -------- 比對用的小工具（沿用你前面已用過的解析邏輯，稍作整合） --------
HEADER_X = "FOG X Parameter:"
HEADER_Y = "FOG Y Parameter:"
HEADER_Z = "FOG Z Parameter:"
HEADER_MIS = "Printing EEPROM FOG Mis-alignment..."
CH_MAP = {"1": "X", "2": "Y", "3": "Z", "4": "MIS"}
GROUP_LABELS = [("X", "FOG X"), ("Y", "FOG Y"), ("Z", "FOG Z"), ("MIS", "Mis-alignment")]

def parse_first_section(lines):
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    mode = None
    rx_param_dot = re.compile(r"^\s*(\d+)\.\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    rx_param_csv = re.compile(r"^\s*(\d+)\s*,\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    rx_mis = re.compile(r"^\s*(\d+)\s*,\s*(-?\d+)\s*$")
    for line in lines:
        s = line.strip()
        if s == HEADER_X:  mode = "X";  continue
        if s == HEADER_Y:  mode = "Y";  continue
        if s == HEADER_Z:  mode = "Z";  continue
        if s == HEADER_MIS: mode = "MIS"; continue
        if mode in {"X", "Y", "Z"}:
            m = rx_param_dot.match(s) or rx_param_csv.match(s)
            if m:
                idx, val = m.groups()
                section[mode][int(idx)] = int(val)
        elif mode == "MIS":
            m = rx_mis.match(s)
            if m:
                idx, val = m.groups()
                section[mode][int(idx)] = int(val)
    return section

def parse_second_section_json(lines):
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    rx_uart = re.compile(r"uart_cmd.*?:\s*([^,\s]+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)")
    rx_json_start = re.compile(r"^\s*\{")
    i = 0
    n = len(lines)
    pending_group = None
    while i < n:
        line = lines[i]
        m = rx_uart.search(line)
        if m:
            ch = m.group(3)
            pending_group = CH_MAP.get(ch)
            i += 1
            while i < n and not rx_json_start.match(lines[i].strip()):
                i += 1
            if i < n and rx_json_start.match(lines[i].strip()):
                buf = [lines[i].strip()]
                while "}" not in lines[i]:
                    i += 1
                    buf.append(lines[i].strip())
                json_text = " ".join(buf)
                try:
                    obj = json.loads(json_text)
                    ordered = OrderedDict(sorted(((int(k), int(v)) for k, v in obj.items()),
                                                 key=lambda kv: kv[0]))
                    if pending_group:
                        section[pending_group] = ordered
                except Exception as e:
                    print(f"[WARN] JSON 解析失敗（{pending_group}）: {e}")
                pending_group = None
            continue
        i += 1
    return section

def parse_mcu_file_text(text):
    """mcu_para 檔案：四個 JSON（X, Y, Z, MIS）每個通常一行。"""
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    json_blobs = []
    buf, capturing = [], False
    for s in lines:
        if s.startswith("{") and s.endswith("}"):
            json_blobs.append(s)
        elif s.startswith("{"):
            capturing = True
            buf = [s]
        elif capturing:
            buf.append(s)
            if s.endswith("}"):
                json_blobs.append(" ".join(buf))
                capturing = False
                buf = []
    order = ["X", "Y", "Z", "MIS"]
    for grp, txt in zip(order, json_blobs):
        obj = json.loads(txt)
        section[grp] = OrderedDict(sorted(((int(k), int(v)) for k, v in obj.items()),
                                          key=lambda kv: kv[0]))
    return section

def diff_dicts(left, right):
    diffs = []
    all_keys = sorted(set(left.keys()) | set(right.keys()))
    for k in all_keys:
        v1 = left.get(k, None)
        v2 = right.get(k, None)
        if v1 != v2:
            diffs.append((k, v1, v2))
    return diffs

def compare_all(fpga_text, mcu_text):
    fpga_lines = fpga_text.splitlines()
    fpga_first  = parse_first_section(fpga_lines)
    fpga_second = parse_second_section_json(fpga_lines)
    mcu = parse_mcu_file_text(mcu_text)

    print("=" * 78)
    print("Compare FPGA(first/list) & FPGA(second/json) against MCU(json)")
    print("=" * 78)

    any_diff = False
    for key, label in GROUP_LABELS:
        d_first  = fpga_first.get(key, OrderedDict())
        d_second = fpga_second.get(key, OrderedDict())
        d_mcu    = mcu.get(key, OrderedDict())

        diffs_first  = diff_dicts(d_first, d_mcu)
        diffs_second = diff_dicts(d_second, d_mcu)

        print(f"\n[{label}]")
        print(f"- FPGA First  (count={len(d_first )})")
        print(f"- FPGA Second (count={len(d_second)})")
        print(f"- MCU         (count={len(d_mcu   )})")

        if not diffs_first and not diffs_second:
            print("  ✔ First vs MCU：No differences.")
            print("  ✔ Second vs MCU：No differences.")
        else:
            if diffs_first:
                any_diff = True
                print("  ✘ First vs MCU differences (index: first → mcu):")
                for idx, v1, v2 in diffs_first:
                    print(f"    - {idx}: {v1} → {v2}")
            else:
                print("  ✔ First vs MCU：No differences.")
            if diffs_second:
                any_diff = True
                print("  ✘ Second vs MCU differences (index: second → mcu):")
                for idx, v1, v2 in diffs_second:
                    print(f"    - {idx}: {v1} → {v2}")
            else:
                print("  ✔ Second vs MCU：No differences.")

    print("\n" + ("ALL MATCH ✅" if not any_diff else "MISMATCHES FOUND ❌"))

# -------- 串口擷取 --------
class SerialCapture(threading.Thread):
    def __init__(self, port, baudrate, silence_sec, global_timeout_sec):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.silence_sec = silence_sec
        self.global_timeout_sec = global_timeout_sec
        self.buffer = bytearray()
        self.stop_event = threading.Event()   # <--- 改名
        self.done_event = threading.Event()   # <--- 改名
        self._exc = None

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=0.05) as ser:
                start = time.time()
                last = time.time()
                while not self.stop_event.is_set():
                    data = ser.read(4096)
                    now = time.time()
                    if data:
                        self.buffer.extend(data)
                        last = now
                    if (now - last) > self.silence_sec:
                        break
                    if (now - start) > self.global_timeout_sec:
                        break
        except Exception as e:
            self._exc = e
        finally:
            self.done_event.set()

    def join_with_exception(self):
        self.join()
        if self._exc:
            raise self._exc

    def text(self, encoding="utf-8"):
        return self.buffer.decode(encoding, errors="ignore")

def main():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fpga_path = SAVE_DIR / f"fpga_para_{ts}.txt"
    mcu_path  = SAVE_DIR / f"mcu_para_{ts}.txt"

    print(f"[INFO] 開始擷取序列埠：FPGA={FPGA_PORT}, MCU={MCU_PORT}, baud={BAUDRATE}")
    print("[HINT] 你可以現在在 PyCharm 按下 Run 後，去幫兩台設備上電。")

    cap_fpga = SerialCapture(FPGA_PORT, BAUDRATE, READ_SILENCE_SEC, GLOBAL_TIMEOUT_SEC)
    cap_mcu  = SerialCapture(MCU_PORT,  BAUDRATE, READ_SILENCE_SEC, GLOBAL_TIMEOUT_SEC)
    cap_fpga.start()
    cap_mcu.start()

    # 等兩路都完成/超時
    cap_fpga.join_with_exception()
    cap_mcu.join_with_exception()

    # 存檔
    fpga_text = cap_fpga.text()
    mcu_text  = cap_mcu.text()

    fpga_path.write_text(fpga_text, encoding="utf-8")
    mcu_path.write_text(mcu_text, encoding="utf-8")

    print(f"[INFO] 已儲存：{fpga_path}")
    print(f"[INFO] 已儲存：{mcu_path}")

    # 直接比對
    compare_all(fpga_text, mcu_text)

if __name__ == "__main__":
    main()
