# drivers/hins_heading_monitor/hins_monitor_validator.py
import logging

class HinsMonitorValidator:
    def __init__(self):
        self.logger = logging.getLogger("drivers.HinsMonitor.Validator")

    def validate(self, packet: list) -> bool:
        if len(packet) != 36: return False

        data = packet[:-2]
        recv_ck_msb = packet[-2]
        recv_ck_lsb = packet[-1]

        sum1, sum2 = 0, 0
        for b in data:
            sum1 = (sum1 + b) & 0xFF  # 使用溢位邏輯 (Modulo 256)
            sum2 = (sum2 + sum1) & 0xFF

        return sum1 == recv_ck_msb and sum2 == recv_ck_lsb