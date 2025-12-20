import tkinter as tk
from tkinter import ttk, messagebox

def parse_hex_bytes(s: str) -> list[int]:
    # allow spaces, commas, newlines, tabs
    tokens = s.replace(",", " ").split()
    if not tokens:
        return []
    out = []
    for t in tokens:
        t = t.strip()
        if t.startswith("0x") or t.startswith("0X"):
            t = t[2:]
        if len(t) == 0 or len(t) > 2:
            raise ValueError(f"Invalid token: '{t}' (expect 1~2 hex digits)")
        out.append(int(t, 16))
    return out

def fletcher_like_hbk_cv7(data: list[int]) -> tuple[int, int]:
    # Matches your expected example:
    # checksum_MSB += byte; checksum_LSB += checksum_MSB; both are uint8 overflow
    msb = 0
    lsb = 0
    for b in data:
        msb = (msb + (b & 0xFF)) & 0xFF
        lsb = (lsb + msb) & 0xFF
    return msb, lsb

def on_compute():
    try:
        s = input_text.get("1.0", "end").strip()
        data = parse_hex_bytes(s)
        if not data:
            messagebox.showwarning("No input", "Please enter hex bytes, e.g.:\n75 65 01 02 02 01")
            return

        msb, lsb = fletcher_like_hbk_cv7(data)
        result = f"{msb:02X} {lsb:02X}"
        result_var.set(result)
        status_var.set(f"OK: {len(data)} bytes")
    except Exception as e:
        result_var.set("")
        status_var.set("Error")
        messagebox.showerror("Parse/Compute error", str(e))

def on_copy():
    r = result_var.get().strip()
    if not r:
        return
    root.clipboard_clear()
    root.clipboard_append(r)
    status_var.set("Copied to clipboard")

root = tk.Tk()
root.title("HBK CV7 Fletcher Checksum (2 bytes)")
root.geometry("520x260")

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

ttk.Label(main, text="Input HEX bytes (space/comma/newline separated):").pack(anchor="w")

input_text = tk.Text(main, height=6, wrap="word")
input_text.pack(fill="x", expand=False, pady=(6, 10))

btn_row = ttk.Frame(main)
btn_row.pack(fill="x")

ttk.Button(btn_row, text="Compute", command=on_compute).pack(side="left")
ttk.Button(btn_row, text="Copy result", command=on_copy).pack(side="left", padx=8)

ttk.Label(main, text="Checksum (MSB LSB):").pack(anchor="w", pady=(12, 0))

result_var = tk.StringVar(value="")
result_entry = ttk.Entry(main, textvariable=result_var, width=20, font=("Consolas", 14))
result_entry.pack(anchor="w", pady=(6, 0))

status_var = tk.StringVar(value="Ready")
ttk.Label(main, textvariable=status_var).pack(anchor="w", pady=(10, 0))

# Prefill with your example
input_text.insert("1.0", "75 65 01 02 02 01")

root.mainloop()
