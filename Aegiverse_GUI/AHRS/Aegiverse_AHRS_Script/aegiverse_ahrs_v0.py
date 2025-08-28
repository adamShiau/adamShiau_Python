# aegiverse_ahrs_v0.py
# 用法：
#   python aegiverse_ahrs_v0.py start COM27
#   python aegiverse_ahrs_v0.py 1 /dev/ttyUSB0
#   python aegiverse_ahrs_v0.py stop COM27
#
# 說明：
# - start：送出開始指令並持續接收與解析封包（CRC 通過才更新印出；失敗則重印上一筆）
# - stop ：僅送出停止指令後結束
#
# 依賴：pyserial
#   pip install pyserial

import argparse
import sys
import time
import struct

try:
    import serial
    import serial.tools.list_ports
except Exception as e:
    print("[ERR] 缺少 pyserial，請先安裝： pip install pyserial")
    sys.exit(2)

# ---------- 協議/定位常數（與你原邏輯一致） ----------
HEADER_KVH = bytes([0xFE, 0x81, 0xFF, 0x55])

SIZE_4       = 4
SIZE_HEADER  = 4
PACKET_PAYLOAD_LEN = 36 + 12       # 你原始程式：getdataPacket(..., 36+12)
PACKET_LEN   = SIZE_HEADER + PACKET_PAYLOAD_LEN  # 52 bytes

# 各欄位相對位置（相對於封包起點，含 header 4B）
POS_WX       = SIZE_HEADER
POS_WY       = POS_WX + SIZE_4
POS_WZ       = POS_WY + SIZE_4
POS_AX       = POS_WZ + SIZE_4
POS_AY       = POS_AX + SIZE_4
POS_AZ       = POS_AY + SIZE_4
POS_PD_TEMP  = POS_AZ + SIZE_4
POS_MCUTIME  = POS_PD_TEMP + SIZE_4
POS_PITCH    = POS_MCUTIME + SIZE_4
POS_ROLL     = POS_PITCH + SIZE_4
POS_YAW      = POS_ROLL + SIZE_4

# 預設 start/stop 指令（三元組：cmd, value, fog_ch）
DEFAULT_START_CMD = (2, 2, 2)
DEFAULT_STOP_CMD  = (2, 4, 2)


# ---------- 低階串口封裝（簡化版 Connector） ----------
class Connector:
    def __init__(self, portName: str, baudRate: int = 230400, timeout_s: float = 0.1):
        self._port = portName
        self._baud = baudRate
        self._ser = serial.Serial()
        self._ser.port = self._port
        self._ser.baudrate = self._baud
        self._ser.timeout = timeout_s
        self._ser.parity = serial.PARITY_NONE
        self._ser.stopbits = serial.STOPBITS_ONE
        self._ser.bytesize = serial.EIGHTBITS

    def connectConn(self) -> bool:
        try:
            self._ser.open()
            return self._ser.is_open
        except serial.SerialException as e:
            print(f"[ERR] 開啟序列埠失敗：{e}")
            return False

    def disconnectConn(self) -> bool:
        try:
            if self._ser.is_open:
                self._ser.close()
            return not self._ser.is_open
        except serial.SerialException as e:
            print(f"[ERR] 關閉序列埠失敗：{e}")
            return False

    def write(self, data: bytes):
        self._ser.write(data)

    def read(self, n: int) -> bytes:
        return self._ser.read(n)

    def readInputBuffer(self) -> int:
        try:
            return self._ser.in_waiting
        except Exception:
            return 0

    def flushInputBuffer(self):
        try:
            self._ser.reset_input_buffer()
        except Exception:
            pass


# ---------- 封包對齊與讀取 ----------
def align_header(ser: Connector, header: bytes) -> bool:
    """讀取資料直到對齊到 header，回傳是否成功對齊。"""
    win = bytearray()
    while True:
        b = ser.read(1)
        if not b:
            # 逾時無資料，讓上層可中斷或重試
            return False
        win += b
        if len(win) > len(header):
            del win[0:len(win)-len(header)]
        if bytes(win) == header:
            return True


def read_exact(ser: Connector, n: int) -> bytes:
    """讀滿 n bytes（多次 read 累積），若逾時回傳目前累積的內容（可能不足）。"""
    buf = bytearray()
    while len(buf) < n:
        chunk = ser.read(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)


def read_one_packet(ser: Connector) -> bytes | None:
    """對齊 header 後讀取完整一包（含 header 與 CRC），成功回 bytes，失敗回 None。"""
    if not align_header(ser, HEADER_KVH):
        return None
    rest = read_exact(ser, PACKET_PAYLOAD_LEN)
    if len(rest) != PACKET_PAYLOAD_LEN:
        return None
    return HEADER_KVH + rest  # 共 52 bytes


# ---------- CRC32（與你提供演算法一致：MSB-first, poly=0x04C11DB7, init=0xFFFFFFFF, no final XOR） ----------
def crc_32(message: bytes, nBytes: int) -> list[int]:
    WIDTH = 32
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x04C11DB7
    remainder = 0xFFFFFFFF
    try:
        for i in range(nBytes):
            remainder ^= (message[i] << (WIDTH - 8))
            for _ in range(8):
                if remainder & TOPBIT:
                    remainder = ((remainder << 1) & 0xFFFFFFFF) ^ POLYNOMIAL
                else:
                    remainder = (remainder << 1) & 0xFFFFFFFF
    except Exception:
        # 保守回傳一個不為零的 remainder
        remainder = 1
    return [(remainder >> 24) & 0xFF, (remainder >> 16) & 0xFF,
            (remainder >> 8) & 0xFF, remainder & 0xFF]


def isCrc32Fail(message: bytes, nBytes: int) -> bool:
    return crc_32(message, nBytes) != [0, 0, 0, 0]


# ---------- 型別/端序轉換 ----------
def IEEE_754_INT2F_R(datain: bytes) -> float:
    """你提供的版本：以 LSB-first 輸入，先反轉，再當作 uint32 重新詮釋為 float（little-endian）。"""
    if len(datain) != 4:
        return -1.0
    shift_data = (datain[3] << 24) | (datain[2] << 16) | (datain[1] << 8) | datain[0]
    try:
        f = struct.unpack('<f', struct.pack('<I', shift_data))[0]
    except struct.error:
        return -1.0
    return f


def IEEE_754_INT2F(datain: bytes) -> float:
    """非反轉版：以 MSB-first 輸入，直接組成 uint32 再詮釋為 float（little-endian pack）。"""
    if len(datain) != 4:
        return -1.0
    shift_data = (datain[0] << 24) | (datain[1] << 16) | (datain[2] << 8) | datain[3]
    try:
        f = struct.unpack('<f', struct.pack('<I', shift_data))[0]
    except struct.error:
        return -1.0
    return f


def convert2Unsign_4B_R(datain: bytes) -> int:
    """4B 小端（LSB-first）轉成 unsigned 32-bit 整數。"""
    if len(datain) != 4:
        return 0
    return (datain[0] |
            (datain[1] << 8) |
            (datain[2] << 16) |
            (datain[3] << 24))


# ---------- 封包資料解析 ----------
def readMP_1Z_ATT(dataPacket: bytes,
                  POS_WX, POS_WY, POS_WZ, POS_AX, POS_AY, POS_AZ,
                  POS_TIME, POS_PDTEMP, POS_PITCH, POS_ROLL, POS_YAW,
                  dataLen: int, PRINT: int = 0):
    temp_wx     = dataPacket[POS_WX:POS_WX + dataLen]
    temp_wy     = dataPacket[POS_WY:POS_WY + dataLen]
    temp_wz     = dataPacket[POS_WZ:POS_WZ + dataLen]
    temp_ax     = dataPacket[POS_AX:POS_AX + dataLen]
    temp_ay     = dataPacket[POS_AY:POS_AY + dataLen]
    temp_az     = dataPacket[POS_AZ:POS_AZ + dataLen]
    temp_pdtemp = dataPacket[POS_PDTEMP:POS_PDTEMP + dataLen]
    temp_time   = dataPacket[POS_TIME:POS_TIME + dataLen]
    temp_pitch  = dataPacket[POS_PITCH:POS_PITCH + dataLen]
    temp_roll   = dataPacket[POS_ROLL:POS_ROLL + dataLen]
    temp_yaw    = dataPacket[POS_YAW:POS_YAW + dataLen]

    wx    = IEEE_754_INT2F_R(temp_wx)
    wy    = IEEE_754_INT2F_R(temp_wy)
    wz    = IEEE_754_INT2F_R(temp_wz)
    ax    = IEEE_754_INT2F_R(temp_ax)
    ay    = IEEE_754_INT2F_R(temp_ay)
    az    = IEEE_754_INT2F_R(temp_az)
    pitch = IEEE_754_INT2F_R(temp_pitch)
    roll  = IEEE_754_INT2F_R(temp_roll)
    yaw   = IEEE_754_INT2F_R(temp_yaw)

    # 你先前提供：PD_TEMP 用非反轉版；若實際也是小端，請改成 IEEE_754_INT2F_R
    pd_temp  = IEEE_754_INT2F(temp_pdtemp)
    mcu_time = convert2Unsign_4B_R(temp_time) / 1000.0  # 單位：毫秒 → 秒

    if PRINT:
        print(f"\n{mcu_time:.3f}, {wx:.6f}, {wy:.6f}, {wz:.6f}, "
              f"{ax:.6f}, {ay:.6f}, {az:.6f}, {pitch:.6f}, "
              f"{roll:.6f}, {yaw:.6f}, {pd_temp:.6f}")

    # 回傳順序固定（你的呼叫端就是照這個順序解包）
    return mcu_time, wx, wy, wz, ax, ay, az, pd_temp, pitch, roll, yaw


# ---------- 指令傳送 ----------
def write_cmd(conn: Connector, cmd: int, value: int, fog_ch: int = 2):
    """照你的協議送指令：AB BA [cmd value(4B) fog_ch] 55 56"""
    if value < 0:
        value = (1 << 32) + value
    payload = bytearray([
        cmd,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8)  & 0xFF,
        value & 0xFF,
        fog_ch,
    ])
    conn.write(b"\xAB\xBA")
    conn.write(payload)
    conn.write(b"\x55\x56")
    time.sleep(0.150)  # 與你原始邏輯一致


# ---------- 輸出格式 ----------
def print_imudata(t, wx, wy, wz, ax, ay, az, pd_temp, pitch, roll, yaw, note: str | None = None):
    line = (f"TIME={t:.3f}s  "
            f"WX={wx:.6f}  WY={wy:.6f}  WZ={wz:.6f}  "
            f"AX={ax:.6f}  AY={ay:.6f}  AZ={az:.6f}  "
            f"PD_TEMP={pd_temp:.3f}  "
            f"PITCH={pitch:.6f}  ROLL={roll:.6f}  YAW={yaw:.6f}")
    if note:
        line += f"  [{note}]"
    print(line, flush=True)


# ---------- 動作流程 ----------
def run_start(port_name: str, baud: int = 230400) -> int:
    conn = Connector(portName=port_name, baudRate=baud)
    if not conn.connectConn():
        return 1

    try:
        # 清空殘留資料
        conn.flushInputBuffer()
        # 送 start
        write_cmd(conn, *DEFAULT_START_CMD)

        last_valid = None  # 保存上一筆通過 CRC 的結果

        print("[INFO] 開始接收（Ctrl+C 停止）")
        while True:
            pkt = read_one_packet(conn)
            if pkt is None:
                # 逾時或對齊失敗，略過讓出 CPU
                time.sleep(0.001)
                continue

            crc_fail = isCrc32Fail(pkt, len(pkt))
            if crc_fail:
                if last_valid is not None:
                    print_imudata(*last_valid, note="CRC FAIL → repeat last")
                else:
                    print("[WARN] CRC FAIL（尚無上一筆可印）")
                continue

            # CRC OK：解析並更新
            parsed = readMP_1Z_ATT(
                pkt,
                POS_WX, POS_WY, POS_WZ,
                POS_AX, POS_AY, POS_AZ,
                POS_MCUTIME, POS_PD_TEMP,
                POS_PITCH, POS_ROLL, POS_YAW,
                4, PRINT=0
            )
            last_valid = parsed
            print_imudata(*parsed)

    except KeyboardInterrupt:
        print("\n[INFO] 停止中 ...")
        try:
            write_cmd(conn, *DEFAULT_STOP_CMD)
        except Exception:
            pass
        conn.disconnectConn()
        print("[INFO] 已送出 stop 並關閉序列埠")
        return 0
    except Exception as e:
        print(f"[ERR] 發生例外：{e}")
        try:
            write_cmd(conn, *DEFAULT_STOP_CMD)
        except Exception:
            pass
        conn.disconnectConn()
        return 2


def run_stop(port_name: str, baud: int = 230400) -> int:
    conn = Connector(portName=port_name, baudRate=baud)
    if not conn.connectConn():
        return 1
    write_cmd(conn, *DEFAULT_STOP_CMD)
    conn.disconnectConn()
    print("[INFO] 已送出 stop 並關閉序列埠")
    return 0


def parse_action(s: str) -> bool:
    """把 start/stop/1/0 轉成布林；True=start, False=stop。"""
    s = s.strip().lower()
    if s in ("1", "start", "on"):
        return True
    if s in ("0", "stop", "off"):
        return False
    raise ValueError("第一個參數需為 start/stop/1/0")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Aegiverse AHRS CLI（CRC 驗證；失敗重印上一筆）")
    p.add_argument("action", help="start/stop 或 1/0")
    p.add_argument("port", help="COM 埠，如 COM27 或 /dev/ttyUSB0")
    p.add_argument("--baud", type=int, default=230400, help="baudrate（預設 230400）")
    args = p.parse_args(argv)

    try:
        start = parse_action(args.action)
    except ValueError as e:
        print("[ERR]", e)
        return 2

    if start:
        return run_start(args.port, args.baud)
    else:
        return run_stop(args.port, args.baud)


if __name__ == "__main__":
    sys.exit(main())
