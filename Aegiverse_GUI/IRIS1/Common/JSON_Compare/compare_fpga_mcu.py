#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from collections import OrderedDict

# -------- 共用設定 --------
HEADER_X = "FOG X Parameter:"
HEADER_Y = "FOG Y Parameter:"
HEADER_Z = "FOG Z Parameter:"
HEADER_MIS = "Printing EEPROM FOG Mis-alignment..."
CH_MAP = {"1": "X", "2": "Y", "3": "Z", "4": "MIS"}
GROUP_LABELS = [("X", "FOG X"), ("Y", "FOG Y"), ("Z", "FOG Z"), ("MIS", "Mis-alignment")]

# -------- 解析 fpga 第一部分（列表印法）--------
def parse_first_section(lines):
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    mode = None
    # 支援兩種格式： "0. 169, type: 0" 與 "0,169,type: 0"
    rx_param_dot = re.compile(r"^\s*(\d+)\.\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    rx_param_csv = re.compile(r"^\s*(\d+)\s*,\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    # Mis-alignment： "0,-1098..."
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

# -------- 解析 fpga 第二部分（JSON 印法）--------
def parse_second_section_json(lines):
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    # 例：uart_cmd, uart_value, ch, condition: 0x81, 2, 4, 1
    rx_uart = re.compile(r"uart_cmd.*?:\s*([^,\s]+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)")
    rx_json_start = re.compile(r"^\s*\{")
    i, n, pending_group = 0, len(lines), None

    while i < n:
        line = lines[i]
        m = rx_uart.search(line)
        if m:
            ch = m.group(3)
            pending_group = CH_MAP.get(ch)
            i += 1
            # 跳過中間標題直到遇到 '{'
            while i < n and not rx_json_start.match(lines[i].strip()):
                i += 1
            if i < n and rx_json_start.match(lines[i].strip()):
                # 你的檔案 JSON 在單行；保險起見收集到 '}'
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

# -------- 解析 mcu_para.txt（4 行 JSON，依序 X, Y, Z, MIS）--------
def parse_mcu_file(path):
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            s = raw.strip()
            if s:
                lines.append(s)

    # 收集每一個以「{」開頭「}」結尾的 JSON；通常一行一個
    json_blobs = []
    buf = []
    capturing = False
    for s in lines:
        if s.startswith("{"):
            capturing = True
            buf = [s]
            if s.endswith("}"):
                json_blobs.append(" ".join(buf))
                capturing = False
                buf = []
        elif capturing:
            buf.append(s)
            if s.endswith("}"):
                json_blobs.append(" ".join(buf))
                capturing = False
                buf = []

    # 期望順序：X, Y, Z, MIS
    order = ["X", "Y", "Z", "MIS"]
    for grp, txt in zip(order, json_blobs):
        obj = json.loads(txt)
        section[grp] = OrderedDict(sorted(((int(k), int(v)) for k, v in obj.items()),
                                          key=lambda kv: kv[0]))
    return section

# -------- 差異比較 --------
def diff_dicts(left, right):
    diffs = []
    all_keys = sorted(set(left.keys()) | set(right.keys()))
    for k in all_keys:
        v1 = left.get(k, None)
        v2 = right.get(k, None)
        if v1 != v2:
            diffs.append((k, v1, v2))
    return diffs

# -------- 主程式 --------
def main(fpga_path, mcu_path):
    with open(fpga_path, "r", encoding="utf-8", errors="ignore") as f:
        fpga_lines = f.read().splitlines()

    # 解析 fpga 的兩部分
    fpga_first  = parse_first_section(fpga_lines)
    fpga_second = parse_second_section_json(fpga_lines)
    # 解析 mcu 檔（四個 JSON）
    mcu = parse_mcu_file(mcu_path)

    print("=" * 78)
    print(f"Compare FPGA(first/list) & FPGA(second/json) against MCU(json)")
    print(f"  FPGA file: {fpga_path}")
    print(f"  MCU  file: {mcu_path}")
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

if __name__ == "__main__":
    from pathlib import Path
    args = sys.argv[1:]

    if len(args) >= 2:
        fpga_path = args[0]
        mcu_path  = args[1]
    else:
        # 預設：腳本同資料夾
        here = Path(__file__).resolve().parent
        fpga_path = str(here / "fpga_para_20250823_214648.txt")
        mcu_path  = str(here / "mcu_para_20250823_192938.txt")
        print(f"[INFO] No arguments. Using default files in script folder:\n"
              f"       FPGA: {fpga_path}\n"
              f"       MCU : {mcu_path}")

    # 檔案存在性檢查（更友善的錯誤訊息）
    from pathlib import Path
    missing = [p for p in [fpga_path, mcu_path] if not Path(p).exists()]
    if missing:
        print("[ERROR] File not found:", ", ".join(missing))
        print("Tip: pass explicit paths, e.g.:")
        print("  python compare_fpga_mcu.py <fpga_para.txt> <mcu_para.txt>")
        sys.exit(1)

    main(fpga_path, mcu_path)
