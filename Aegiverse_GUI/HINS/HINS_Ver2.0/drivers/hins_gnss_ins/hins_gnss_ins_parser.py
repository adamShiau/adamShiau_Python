# drivers/hins_gnss_ins/hins_gnss_ins_parser.py
# -*- coding:UTF-8 -*-
import logging
from .mip_handlers import MIP_SET_REGISTRY


class HinsGnssInsParser:
    def __init__(self, device_name="HinsGnssIns"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Parser")

    def parse(self, mip_data: list) -> dict:
        """ 剝洋蔥第三層：解析 MIP 數據包 (工廠模式版) """
        if len(mip_data) < 6: return {}

        desc_set = mip_data[2]
        payload = mip_data[4:-2]

        results = {"desc_set": hex(desc_set), "fields": []}

        # 1. 根據 Descriptor Set (如 0x0C) 取得對應的處理物件
        set_handler = MIP_SET_REGISTRY.get(desc_set)

        cursor = 0
        while cursor < len(payload):
            f_len = payload[cursor]
            if f_len == 0 or cursor + f_len > len(payload): break

            f_desc = payload[cursor + 1]
            f_data = payload[cursor + 2: cursor + f_len]

            # 2. 委託該處理物件進行解析
            field_res = {}
            if set_handler:
                try:
                    field_res = set_handler.parse_field(f_desc, f_data)
                except Exception as e:
                    field_res = {"error": str(e), "raw": f_data.hex()}
            else:
                # 若無對應 Set Handler (例如尚未實作的 0x80)
                field_res = {"raw": f_data.hex()}

            # 3. 統一加上 Descriptor 標籤
            field_res["descriptor"] = hex(f_desc)
            results["fields"].append(field_res)

            cursor += f_len

        return results