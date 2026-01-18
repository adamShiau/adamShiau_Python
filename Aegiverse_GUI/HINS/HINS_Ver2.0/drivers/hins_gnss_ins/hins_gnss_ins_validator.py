# drivers/hins_gnss_ins/hins_gnss_ins_validator.py
import logging

class HinsGnssInsValidator:
    def __init__(self, device_name="HinsGnssIns"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Validator")

    def validate(self, packet: list) -> bool:
        if len(packet) < 8: return False

        # 範圍：從 Index 1 (Type) 開始到倒數第 3 個 (Payload 結束)
        data_to_check = packet[1:-2]
        ck_a = 0
        ck_b = 0
        for b in data_to_check:
            ck_a = (ck_a + b) % 255
            ck_b = (ck_b + ck_a) % 255

        # 判斷校驗碼是否匹配
        if ck_a == packet[-2] and ck_b == packet[-1]:
            return True
        else:
            # 使用 print 確保您在測試時看得到錯誤
            print(f"\n[Checksum Error] CMD:{hex(packet[2])} | 算出:{ck_a:02X} {ck_b:02X} | 封包內:{packet[-2]:02X} {packet[-1]:02X}")
            return False