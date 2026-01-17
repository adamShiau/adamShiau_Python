import tkinter as tk
from tkinter import ttk, messagebox

def parse_hex_bytes(s: str) -> list[int]:
    # 允許空格, 逗號, 換行, Tab
    tokens = s.replace(",", " ").split()
    if not tokens:
        return []
    out = []
    for t in tokens:
        t = t.strip()
        if t.startswith("0x") or t.startswith("0X"):
            t = t[2:]
        if len(t) == 0 or len(t) > 2:
            raise ValueError(f"無效的位元組: '{t}' (請輸入 1~2 位 16 進位數)")
        out.append(int(t, 16))
    return out

def calc_mip_fletcher(data: list[int]):
    """ MIP 模式: 8-bit 溢位累加 (Modulo 256) """
    sum1 = 0
    sum2 = 0
    for b in data:
        sum1 = (sum1 + (b & 0xFF)) & 0xFF
        sum2 = (sum2 + sum1) & 0xFF
    return sum1, sum2

def calc_v1_fletcher(data: list[int]):
    """ V1 模式: 標準 Fletcher16 (Modulo 255) """
    sum1 = 0
    sum2 = 0
    for b in data:
        sum1 = (sum1 + b) % 255
        sum2 = (sum2 + sum1) % 255
    return sum1, sum2

def on_compute():
    try:
        s = input_text.get("1.0", "end").strip()
        data = parse_hex_bytes(s)
        if not data:
            messagebox.showwarning("無輸入", "請輸入 HEX 字串")
            return

        mode = mode_var.get()
        if mode == "MIP":
            s1, s2 = calc_mip_fletcher(data)
            result = f"{s1:02X} {s2:02X}"
            label_var.set("MIP Checksum (MSB LSB):")
        else:
            s1, s2 = calc_v1_fletcher(data)
            result = f"{s1:02X} {s2:02X}"
            label_var.set("V1 Checksum (Sum1 Sum2):")

        result_var.set(result)
        status_var.set(f"成功: 已計算 {len(data)} Bytes (模式: {mode})")
    except Exception as e:
        result_var.set("")
        status_var.set("錯誤")
        messagebox.showerror("計算錯誤", str(e))

def on_copy():
    r = result_var.get().strip()
    if not r: return
    root.clipboard_clear()
    root.clipboard_append(r)
    status_var.set("已複製到剪貼簿")

# GUI 設定
root = tk.Tk()
root.title("HINS MCU Checksum 工具 (V1 / MIP)")
root.geometry("550x350")

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

# 模式選擇
mode_frame = ttk.LabelFrame(main, text=" 選擇計算模式 ", padding=8)
mode_frame.pack(fill="x", pady=(0, 10))

mode_var = tk.StringVar(value="MIP")
ttk.Radiobutton(mode_frame, text="MIP 模式 (Modulo 256 / HBK)", variable=mode_var, value="MIP").pack(side="left", padx=10)
ttk.Radiobutton(mode_frame, text="V1 模式 (Modulo 255 / 標準)", variable=mode_var, value="V1").pack(side="left", padx=10)

ttk.Label(main, text="輸入 HEX 位元組 (空格或逗號分隔):").pack(anchor="w")
input_text = tk.Text(main, height=6, wrap="word")
input_text.pack(fill="x", pady=(6, 10))

btn_row = ttk.Frame(main)
btn_row.pack(fill="x")
ttk.Button(btn_row, text="計算 Checksum", command=on_compute).pack(side="left")
ttk.Button(btn_row, text="複製結果", command=on_copy).pack(side="left", padx=8)

label_var = tk.StringVar(value="Checksum:")
ttk.Label(main, textvariable=label_var).pack(anchor="w", pady=(12, 0))

result_var = tk.StringVar(value="")
result_entry = ttk.Entry(main, textvariable=result_var, width=20, font=("Consolas", 14))
result_entry.pack(anchor="w", pady=(6, 0))

status_var = tk.StringVar(value="準備就緒")
ttk.Label(main, textvariable=status_var).pack(anchor="w", pady=(10, 0))

root.mainloop()