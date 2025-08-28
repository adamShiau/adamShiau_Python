# aegiverse_ahrs.py
# 用法（Windows / Linux）：
#   python aegiverse_ahrs.py start COM27
#   python aegiverse_ahrs.py 1 COM27
#   python aegiverse_ahrs.py stop COM27
#
# 依賴：pyserial
#   pip install pyserial

import argparse
import sys
import time
import struct

try:
    import serial
except Exception:
    print("pyserial not installed. Run: pip install pyserial", file=sys.stderr)
    sys.exit(2)

# ---- 協議常數 ----
HEADER = bytes([0xFE, 0x81, 0xFF, 0x55])
SIZE_4 = 4
PACKET_PAYLOAD_LEN = 36 + 12        # payload(含 CRC 4B)
PACKET_LEN = 4 + PACKET_PAYLOAD_LEN # header(4) + payload

# 欄位位置（相對封包起點）
POS_WX      = 4
POS_WY      = POS_WX + SIZE_4
POS_WZ      = POS_WY + SIZE_4
POS_AX      = POS_WZ + SIZE_4
POS_AY      = POS_AX + SIZE_4
POS_AZ      = POS_AY + SIZE_4
POS_PD_TEMP = POS_AZ + SIZE_4
POS_TIME    = POS_PD_TEMP + SIZE_4
POS_PITCH   = POS_TIME + SIZE_4
POS_ROLL    = POS_PITCH + SIZE_4
POS_YAW     = POS_ROLL + SIZE_4

# 啟停指令（cmd, value, fog_ch）
START_CMD = (2, 2, 2)
STOP_CMD  = (2, 4, 2)


# ---- 小型連接器 ----
class Connector:
    def __init__(self, port: str, baud: int = 230400, timeout_s: float = 0.1):
        self._ser = serial.Serial()
        self._ser.port = port
        self._ser.baudrate = baud
        self._ser.timeout = timeout_s
        self._ser.parity = serial.PARITY_NONE
        self._ser.stopbits = serial.STOPBITS_ONE
        self._ser.bytesize = serial.EIGHTBITS

    def open(self) -> bool:
        try:
            self._ser.open()
            return self._ser.is_open
        except serial.SerialException:
            return False

    def close(self) -> None:
        try:
            if self._ser.is_open:
                self._ser.close()
        except serial.SerialException:
            pass

    def write(self, data: bytes) -> None:
        self._ser.write(data)

    def read(self, n: int) -> bytes:
        return self._ser.read(n)

    def flush_in(self) -> None:
        try:
            self._ser.reset_input_buffer()
        except Exception:
            pass


# ---- 封包 I/O ----
def write_cmd(conn: Connector, cmd: int, value: int, fog_ch: int = 2):
    if value < 0:
        value = (1 << 32) + value
    payload = bytearray([
        cmd,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8)  & 0xFF,
        value & 0xFF,
        fog_ch
    ])
    conn.write(b"\xAB\xBA")
    conn.write(payload)
    conn.write(b"\x55\x56")
    time.sleep(0.150)

def align_header(conn: Connector) -> bool:
    win = bytearray()
    while True:
        b = conn.read(1)
        if not b:
            return False  # timeout
        win += b
        if len(win) > len(HEADER):
            del win[0:len(win)-len(HEADER)]
        if bytes(win) == HEADER:
            return True

def read_exact(conn: Connector, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.read(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)

def read_packet(conn: Connector) -> bytes | None:
    if not align_header(conn):
        return None
    rest = read_exact(conn, PACKET_PAYLOAD_LEN)
    if len(rest) != PACKET_PAYLOAD_LEN:
        return None
    return HEADER + rest


# ---- CRC（MSB-first, poly=0x04C11DB7, init=0xFFFFFFFF, no final XOR）----
def crc_32(message: bytes, n: int) -> list[int]:
    WIDTH = 32
    TOPBIT = 1 << (WIDTH - 1)
    POLY = 0x04C11DB7
    r = 0xFFFFFFFF
    for i in range(n):
        r ^= (message[i] << (WIDTH - 8))
        for _ in range(8):
            if r & TOPBIT:
                r = ((r << 1) & 0xFFFFFFFF) ^ POLY
            else:
                r = (r << 1) & 0xFFFFFFFF
    return [(r >> 24) & 0xFF, (r >> 16) & 0xFF, (r >> 8) & 0xFF, r & 0xFF]

def is_crc_fail(msg: bytes) -> bool:
    return crc_32(msg, len(msg)) != [0, 0, 0, 0]


# ---- 端序/轉型 ----
def f_from_le_bytes_reversed(b4: bytes) -> float:
    # 來源為 LSB-first 4 bytes：先反向再解釋為 float
    if len(b4) != 4:
        return -1.0
    u = (b4[3] << 24) | (b4[2] << 16) | (b4[1] << 8) | b4[0]
    return struct.unpack('<f', struct.pack('<I', u))[0]

def f_from_be_bytes(b4: bytes) -> float:
    # 來源為 MSB-first 4 bytes
    if len(b4) != 4:
        return -1.0
    u = (b4[0] << 24) | (b4[1] << 16) | (b4[2] << 8) | b4[3]
    return struct.unpack('<f', struct.pack('<I', u))[0]

def u32_from_le(b4: bytes) -> int:
    if len(b4) != 4:
        return 0
    return b4[0] | (b4[1] << 8) | (b4[2] << 16) | (b4[3] << 24)


# ---- 解析一包 → (TIME, WX, WY, WZ, AX, AY, AZ, PD_TEMP, PITCH, ROLL, YAW) ----
def parse_packet(pkt: bytes):
    wx  = f_from_le_bytes_reversed(pkt[POS_WX:POS_WX+4])
    wy  = f_from_le_bytes_reversed(pkt[POS_WY:POS_WY+4])
    wz  = f_from_le_bytes_reversed(pkt[POS_WZ:POS_WZ+4])
    ax  = f_from_le_bytes_reversed(pkt[POS_AX:POS_AX+4])
    ay  = f_from_le_bytes_reversed(pkt[POS_AY:POS_AY+4])
    az  = f_from_le_bytes_reversed(pkt[POS_AZ:POS_AZ+4])
    # 若 PD_TEMP 實際也是小端，改成 f_from_le_bytes_reversed
    pd  = f_from_be_bytes(pkt[POS_PD_TEMP:POS_PD_TEMP+4])
    tm  = u32_from_le(pkt[POS_TIME:POS_TIME+4]) / 1000.0
    pt  = f_from_le_bytes_reversed(pkt[POS_PITCH:POS_PITCH+4])
    rl  = f_from_le_bytes_reversed(pkt[POS_ROLL:POS_ROLL+4])
    yw  = f_from_le_bytes_reversed(pkt[POS_YAW:POS_YAW+4])
    return tm, wx, wy, wz, ax, ay, az, pd, pt, rl, yw


# ---- 主流程 ----
def parse_action(s: str) -> bool:
    s = s.strip().lower()
    if s in ("1", "start", "on"):
        return True
    if s in ("0", "stop", "off"):
        return False
    raise ValueError("action must be start/stop or 1/0")

def run_start(port: str, baud: int) -> int:
    conn = Connector(port, baud)
    if not conn.open():
        return 1
    try:
        conn.flush_in()
        write_cmd(conn, *START_CMD)

        last = None  # 最近一筆通過 CRC 的資料
        while True:
            pkt = read_packet(conn)
            if pkt is None:
                # timeout 或對齊失敗：略過
                continue
            if is_crc_fail(pkt):
                if last is not None:
                    # 失敗：印上一筆
                    print_csv(*last)
                # 若尚無上一筆，什麼都不印
                continue
            # 成功：解析並印出
            parsed = parse_packet(pkt)
            last = parsed
            print_csv(*parsed)
    except KeyboardInterrupt:
        try:
            write_cmd(conn, *STOP_CMD)
        except Exception:
            pass
        conn.close()
        return 0
    except Exception:
        try:
            write_cmd(conn, *STOP_CMD)
        except Exception:
            pass
        conn.close()
        return 2

def run_stop(port: str, baud: int) -> int:
    conn = Connector(port, baud)
    if not conn.open():
        return 1
    write_cmd(conn, *STOP_CMD)
    conn.close()
    return 0

def print_csv(t, wx, wy, wz, ax, ay, az, pd, pt, rl, yw):
    # 依你原來格式：TIME 3 位小數、PD_TEMP 3，其餘 6
    sys.stdout.write(f"{t:.3f},{wx:.6f},{wy:.6f},{wz:.6f},"
                     f"{ax:.6f},{ay:.6f},{az:.6f},"
                     f"{pd:.3f},"
                     f"{pt:.6f},{rl:.6f},{yw:.6f}\n")
    sys.stdout.flush()

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Aegiverse AHRS CLI (CSV output)")
    ap.add_argument("action", help="start/stop 或 1/0")
    ap.add_argument("port",   help="COM 埠，如 COM27 或 /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=230400, help="baudrate (default 230400)")
    args = ap.parse_args(argv)
    try:
        do_start = parse_action(args.action)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    return run_start(args.port, args.baud) if do_start else run_stop(args.port, args.baud)

if __name__ == "__main__":
    sys.exit(main())
