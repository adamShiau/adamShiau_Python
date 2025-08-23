#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from collections import OrderedDict

HEADER_X = "FOG X Parameter:"
HEADER_Y = "FOG Y Parameter:"
HEADER_Z = "FOG Z Parameter:"
HEADER_MIS = "Printing EEPROM FOG Mis-alignment..."

CH_MAP = {"1": "X", "2": "Y", "3": "Z", "4": "MIS"}

def parse_first_section(lines):
    """解析第一部分 (列表印法) → dict: {'X': {idx:val}, 'Y':..., 'Z':..., 'MIS':...}"""
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}
    mode = None

    # 同時支援兩種印法：
    # 1) "0. 169, type: 0"
    rx_param_dot = re.compile(r"^\s*(\d+)\.\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    # 2) "0,169,type: 0"
    rx_param_csv = re.compile(r"^\s*(\d+)\s*,\s*(-?\d+)\s*,\s*type:\s*-?\d+\s*$")
    # Mis-alignment: "0,-1098..."
    rx_mis = re.compile(r"^\s*(\d+)\s*,\s*(-?\d+)\s*$")

    for line in lines:
        s = line.strip()
        if s == HEADER_X:
            mode = "X"; continue
        if s == HEADER_Y:
            mode = "Y"; continue
        if s == HEADER_Z:
            mode = "Z"; continue
        if s == HEADER_MIS:
            mode = "MIS"; continue

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
    """
    解析第二部分 (JSON)。
    強化點：
      - 從 'uart_cmd, ... : <opcode>, <value>, <ch>, <cond>' 取出 ch
      - 允許中間有 'CMD_DUMP_FOG:' / 'CMD_DUMP_MIS:' 等標題行
      - 直到遇到以 '{' 開頭的行才開始讀 JSON
    """
    section = {"X": OrderedDict(), "Y": OrderedDict(), "Z": OrderedDict(), "MIS": OrderedDict()}

    # 取出冒號後四個欄位：例 '...: 0x81, 2, 4, 1'
    rx_uart = re.compile(r"uart_cmd.*?:\s*([^,\s]+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)")
    rx_json_start = re.compile(r"^\s*\{")

    i = 0
    n = len(lines)
    pending_group = None

    while i < n:
        line = lines[i]
        m = rx_uart.search(line)
        if m:
            ch = m.group(3)  # 第三個欄位是 ch
            pending_group = CH_MAP.get(ch)
            i += 1

            # 跳過可能存在的標題行，直到真的遇到 JSON '{'
            while i < n and not rx_json_start.match(lines[i].strip()):
                i += 1

            if i < n and rx_json_start.match(lines[i].strip()):
                json_line = lines[i].strip()
                # 若 JSON 可能跨行，收集到 '}' 為止（你目前檔案是一行就結束）
                buf = [json_line]
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
                    print(f"[WARN] JSON 解析失敗 ({pending_group}): {e}")

                pending_group = None
            continue

        i += 1

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


def main(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    first = parse_first_section(lines)
    second = parse_second_section_json(lines)

    groups = [("X", "FOG X"), ("Y", "FOG Y"), ("Z", "FOG Z"), ("MIS", "Mis-alignment")]

    print("=" * 72)
    print(f"Comparing parameters: {path}")
    print("=" * 72)

    any_diff = False
    for key, label in groups:
        d1 = first.get(key, OrderedDict())
        d2 = second.get(key, OrderedDict())
        diffs = diff_dicts(d1, d2)

        print(f"\n[{label}]")
        print(f"- First count:  {len(d1)}")
        print(f"- Second count: {len(d2)}")
        if not diffs:
            print("  ✔ No differences.")
        else:
            any_diff = True
            print("  ✘ Differences:")
            for idx, v1, v2 in diffs:
                print(f"    - {idx}: {v1} → {v2}")

    print("\n" + ("ALL MATCH ✅" if not any_diff else "MISMATCHES FOUND ❌"))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "fpga_para2.txt"
    main(path)
