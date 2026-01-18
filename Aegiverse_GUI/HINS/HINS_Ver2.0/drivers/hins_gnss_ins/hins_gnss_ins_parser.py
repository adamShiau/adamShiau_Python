# drivers/hins_gnss_ins/hins_gnss_ins_parser.py
# -*- coding:UTF-8 -*-
import logging

class HinsGnssInsParser:
    def __init__(self, device_name="HinsGnssIns"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Parser")

    def parse(self, mip_data: list) -> dict:
        """ 解析 MIP (75 65...) """
        if len(mip_data) < 4 or mip_data[0] != 0x75 or mip_data[1] != 0x65:
            return {"RAW": mip_data}

        # MIP Header: 75 65 [DescSet] [Len]
        desc_set = mip_data[2]
        # MIP Field: [Len] [Desc] [Data...]
        # 以 GPIO 回傳為例: 0A 04 F1 41 00 06 C1 01 05 21 00 14 (依據您的數據)

        res = {
            "MIP_DESC_SET": hex(desc_set),
            "MIP_PAYLOAD": mip_data[4:],
            "RAW": mip_data
        }
        return res