# drivers/hins_heading_monitor/hins_monitor_parser.py
import struct
import logging

class HinsMonitorParser:
    def __init__(self):
        self.logger = logging.getLogger("drivers.HinsMonitor.Parser")
        # [更新] 2B(Header), B(Fix), H(Status), H(Valid), 3f(Floats), d(Double), 3H(U16s), B(Case), 2B(CK)
        # 長度計算: 2 + 1 + 2 + 2 + (4*3) + 8 + (2*3) + 1 + 2 = 36 Bytes
        self.struct_fmt = "<2B B H H 3f d H H H B 2B"

    def parse(self, packet: list) -> dict:
        try:
            unpacked = struct.unpack(self.struct_fmt, bytes(packet))
            # print(f"Parser Raw Unpacked: {unpacked}")

            result = {
                "type": "MCU_MONITOR",
                "fix_type": unpacked[2],
                "status_flag": unpacked[3],      # [新增] 插入的新欄位
                "valid_flag_da": unpacked[4],    # 位移
                "heading_da": unpacked[5],      # 位移
                "imu_heading": unpacked[6],     # 位移
                "offset": unpacked[7],          # 位移
                "gps_tow": unpacked[8],         # 位移
                "filter_state": unpacked[9],    # 位移
                "dynamic_mode": unpacked[10],   # 位移
                "status_82": unpacked[11],      # 位移
                "case_flag": unpacked[12]       # 位移
            }
            # print(f"Parser Output: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return {}