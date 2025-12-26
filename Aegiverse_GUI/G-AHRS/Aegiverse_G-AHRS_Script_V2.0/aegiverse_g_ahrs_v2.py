import argparse
import sys
import time
import struct

try:
    import serial
except Exception:
    print("pyserial not installed. Run: pip install pyserial", file=sys.stderr)
    sys.exit(2)
import serial.tools.list_ports

__version__ = "2.0"
__author__  = "Adam Shiau"
__date__    = "2025-12-18"

# =========================
# Protocol constants
# =========================
AHRS_HEADER = bytes([0xFE, 0x81, 0xFF, 0x55])
GNSS_HEADER = bytes([0xFE, 0x82, 0xFF, 0x55])

SIZE_4 = 4
PACKET_PAYLOAD_LEN = 49              # payload (includes CRC 4B)
PACKET_LEN = 4 + PACKET_PAYLOAD_LEN  # header(4) + payload

# Start/Stop commands (cmd, value, fog_ch)
START_CMD = (2, 2, 2)
STOP_CMD  = (2, 4, 2)

# =========================
# Connector
# =========================
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

# =========================
# Packet I/O
# =========================
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

def align_header(conn: Connector, header: bytes) -> bool:
    win = bytearray()
    while True:
        b = conn.read(1)
        if not b:
            return False
        win += b
        if len(win) > len(header):
            del win[0:len(win)-len(header)]
        if bytes(win) == header:
            return True

def read_exact(conn: Connector, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = conn.read(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)

def read_packet(conn: Connector, header: bytes) -> bytes | None:
    if not align_header(conn, header):
        return None
    rest = read_exact(conn, PACKET_PAYLOAD_LEN)
    if len(rest) != PACKET_PAYLOAD_LEN:
        return None
    return header + rest

# =========================
# CRC
# =========================
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

# =========================
# Endianness helpers
# =========================
def f32_from_lsb_first_4bytes(b4: bytes) -> float:
    if len(b4) != 4:
        return float("nan")
    return struct.unpack("<f", b4)[0]

def f32_from_msb_first_4bytes(b4: bytes) -> float:
    if len(b4) != 4:
        return float("nan")
    return struct.unpack(">f", b4)[0]

def u32_from_lsb_first_4bytes(b4: bytes) -> int:
    if len(b4) != 4:
        return 0
    return b4[0] | (b4[1] << 8) | (b4[2] << 16) | (b4[3] << 24)

def u16_from_lsb_first_2bytes(b2: bytes) -> int:
    if len(b2) != 2:
        return 0
    return b2[0] | (b2[1] << 8)

def f64_from_lsb_first_8bytes(b8: bytes) -> float:
    if len(b8) != 8:
        return float("nan")
    return struct.unpack("<d", b8)[0]

# =========================
# AHRS packet parsing (unchanged)
# =========================
POS_WX      = 4
POS_WY      = POS_WX + 4
POS_WZ      = POS_WY + 4
POS_AX      = POS_WZ + 4
POS_AY      = POS_AX + 4
POS_AZ      = POS_AY + 4
POS_PD_TEMP = POS_AZ + 4
POS_TIME    = POS_PD_TEMP + 4
POS_PITCH   = POS_TIME + 4
POS_ROLL    = POS_PITCH + 4
POS_YAW     = POS_ROLL + 4

def parse_packet_ahrs(pkt: bytes):
    def f_from_le_bytes_reversed(b4: bytes) -> float:
        if len(b4) != 4:
            return float("nan")
        u = (b4[3] << 24) | (b4[2] << 16) | (b4[1] << 8) | b4[0]
        return struct.unpack('<f', struct.pack('<I', u))[0]

    wx  = f_from_le_bytes_reversed(pkt[POS_WX:POS_WX+4])
    wy  = f_from_le_bytes_reversed(pkt[POS_WY:POS_WY+4])
    wz  = f_from_le_bytes_reversed(pkt[POS_WZ:POS_WZ+4])
    ax  = f_from_le_bytes_reversed(pkt[POS_AX:POS_AX+4])
    ay  = f_from_le_bytes_reversed(pkt[POS_AY:POS_AY+4])
    az  = f_from_le_bytes_reversed(pkt[POS_AZ:POS_AZ+4])

    pd  = f32_from_msb_first_4bytes(pkt[POS_PD_TEMP:POS_PD_TEMP+4])

    tm  = u32_from_lsb_first_4bytes(pkt[POS_TIME:POS_TIME+4]) / 1000.0
    pt  = f_from_le_bytes_reversed(pkt[POS_PITCH:POS_PITCH+4])
    rl  = f_from_le_bytes_reversed(pkt[POS_ROLL:POS_ROLL+4])
    yw  = f_from_le_bytes_reversed(pkt[POS_YAW:POS_YAW+4])
    return tm, wx, wy, wz, ax, ay, az, pd, pt, rl, yw

def print_csv_ahrs(t, wx, wy, wz, ax, ay, az, pd, pt, rl, yw):
    sys.stdout.write(
        f"{t:.3f},{wx:.6f},{wy:.6f},{wz:.6f},"
        f"{ax:.6f},{ay:.6f},{az:.6f},"
        f"{pd:.3f},"
        f"{pt:.6f},{rl:.6f},{yw:.6f}\n"
    )
    sys.stdout.flush()

# =========================
# GNSS packet parsing
# =========================
GNSS_POS_LAT       = 4
GNSS_POS_LON       = 12
GNSS_POS_ALT       = 20
GNSS_POS_TS        = 24
GNSS_POS_UTC_H     = 28
GNSS_POS_UTC_MIN   = 29
GNSS_POS_UTC_S     = 30
GNSS_POS_UTC_MS    = 31
GNSS_POS_UTC_DAY   = 33
GNSS_POS_UTC_MON   = 34
GNSS_POS_UTC_YEAR  = 35
GNSS_POS_TEMP      = 37
GNSS_POS_MCU_TIME  = 41
GNSS_POS_STATUS    = 45

def parse_packet_gnss(pkt: bytes):
    lat = f64_from_lsb_first_8bytes(pkt[GNSS_POS_LAT:GNSS_POS_LAT+8])
    lon = f64_from_lsb_first_8bytes(pkt[GNSS_POS_LON:GNSS_POS_LON+8])
    alt = f32_from_lsb_first_4bytes(pkt[GNSS_POS_ALT:GNSS_POS_ALT+4])

    # ONLY CHANGE: ms -> s
    mcu_time_ms = (
        u32_from_lsb_first_4bytes(
            pkt[GNSS_POS_MCU_TIME:GNSS_POS_MCU_TIME+4]
        ) / 1000.0
    )

    utc_h = pkt[GNSS_POS_UTC_H]
    utc_m = pkt[GNSS_POS_UTC_MIN]
    utc_s = pkt[GNSS_POS_UTC_S]
    utc_ms = u16_from_lsb_first_2bytes(pkt[GNSS_POS_UTC_MS:GNSS_POS_UTC_MS+2])

    utc_day = pkt[GNSS_POS_UTC_DAY]
    utc_mon = pkt[GNSS_POS_UTC_MON]
    utc_year = u16_from_lsb_first_2bytes(pkt[GNSS_POS_UTC_YEAR:GNSS_POS_UTC_YEAR+2])

    gps_status = pkt[GNSS_POS_STATUS]

    return (mcu_time_ms, lat, lon, alt,
            utc_year, utc_mon, utc_day,
            utc_h, utc_m, utc_s, utc_ms,
            gps_status)

def print_csv_gnss(mcu_time_ms, latitude, longitude, altitude,
                   utc_year, utc_month, utc_day,
                   utc_hour, utc_minute, utc_second, utc_millisecond,
                   gps_status_code):
    sys.stdout.write(
        f"{mcu_time_ms:.3f},"
        f"{latitude:.6f},{longitude:.6f},{altitude:.2f},"
        f"{utc_year},{utc_month},{utc_day},"
        f"{utc_hour},{utc_minute},{utc_second},{utc_millisecond},"
        f"{gps_status_code}\n"
    )
    sys.stdout.flush()

# =========================
# Main flows (UNCHANGED)
# =========================
def list_comports(only_names: bool = True) -> int:
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return 1
    if only_names:
        for p in ports:
            print(p.device)
    else:
        for p in ports:
            print(f"{p.device}\t{p.description}\t{p.hwid}")
    return 0

def parse_mode(action: str) -> int:
    s = action.strip().lower()
    if s == "list":
        return -1
    if s in ("0", "stop", "off"):
        return 0
    if s in ("1",):
        return 1
    if s in ("2",):
        return 2
    raise ValueError("action must be 0/1/2 or 'list'")

def run_stop(port: str, baud: int) -> int:
    conn = Connector(port, baud)
    if not conn.open():
        return 1
    write_cmd(conn, *STOP_CMD)
    conn.close()
    return 0

def run_start(port: str, baud: int, mode: int) -> int:
    conn = Connector(port, baud)
    if not conn.open():
        return 1
    try:
        conn.flush_in()
        write_cmd(conn, *START_CMD)

        header = AHRS_HEADER if mode == 1 else GNSS_HEADER

        last = None
        t0 = None

        while True:
            pkt = read_packet(conn, header)
            if pkt is None:
                continue
            if is_crc_fail(pkt):
                if last is not None:
                    if mode == 1:
                        print_csv_ahrs(*last)
                    else:
                        print_csv_gnss(*last)
                continue

            if mode == 1:
                parsed = parse_packet_ahrs(pkt)
            else:
                parsed = parse_packet_gnss(pkt)

            tm = parsed[0]
            if t0 is None:
                t0 = tm
            parsed = (tm - t0,) + parsed[1:]
            last = parsed

            if mode == 1:
                print_csv_ahrs(*parsed)
            else:
                print_csv_gnss(*parsed)

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

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Aegiverse CLI (CSV output)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("action", help="0=stop, 1=AHRS packet, 2=GNSS packet, or 'list'")
    ap.add_argument("port", nargs="?", help="COM port, e.g. COM27 or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=230400, help="baudrate (default 230400)")
    args = ap.parse_args(argv)

    try:
        mode = parse_mode(args.action)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    if mode == -1:
        return list_comports(only_names=True)

    if not args.port:
        print("Please provide a port name, e.g. COM27 or /dev/ttyUSB0", file=sys.stderr)
        return 2

    if mode == 0:
        return run_stop(args.port, args.baud)
    return run_start(args.port, args.baud, mode)

if __name__ == "__main__":
    sys.exit(main())
