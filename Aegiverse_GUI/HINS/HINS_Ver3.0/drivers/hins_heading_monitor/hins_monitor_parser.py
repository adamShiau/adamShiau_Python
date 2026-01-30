# drivers/hins_heading_monitor/hins_monitor_parser.py
import struct
import logging

class HinsMonitorParser:
    def __init__(self):
        self.logger = logging.getLogger("drivers.HinsMonitor.Parser")
        # 2B(Header), B(Fix), H(Valid), 3f(Floats), d(Double), 3H(U16s), B(Case), 2B(CK)
        # 長度計算: 2 + 1 + 2 + (4*3) + 8 + (2*3) + 1 + 2 = 34 Bytes
        self.struct_fmt = "<2B B H 3f d H H H B 2B"

    def parse(self, packet: list) -> dict:
        try:
            unpacked = struct.unpack(self.struct_fmt, bytes(packet))
            return {
                "type": "MCU_MONITOR",
                "fix_type": unpacked[2],
                "valid_flag_da": unpacked[3],
                "heading_da": unpacked[4],
                "imu_heading": unpacked[5],
                "offset": unpacked[6],
                "gps_tow": unpacked[7],
                "filter_state": unpacked[8],
                "dynamic_mode": unpacked[9],
                "status_82": unpacked[10],
                "case_flag": unpacked[11]
            }
        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return {}