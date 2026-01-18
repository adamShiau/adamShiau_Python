# drivers/hins_gnss_ins/hins_gnss_ins_parser.py
# -*- coding:UTF-8 -*-
import logging
import struct


class HinsGnssInsParser:
    def __init__(self, device_name="HinsGnssIns"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Parser")

        # 建立解析規則映射表: {(DescriptorSet, FieldDescriptor): handler_function}
        # 這裡決定了什麼 Descriptor 用什麼規則解
        self.__handlers = {
            (0x0C, 0xC1): self._parse_gpio_config,  # GPIO Config Response
            (0x0C, 0xF1): self._parse_ack_nack,  # Common ACK/NACK
        }

    def parse(self, mip_data: list) -> dict:
        """ 剝洋蔥第三層：解析 MIP 數據包 """
        if len(mip_data) < 6: return {}

        desc_set = mip_data[2]
        payload = mip_data[4:-2]

        results = {"desc_set": hex(desc_set), "fields": []}

        cursor = 0
        while cursor < len(payload):
            f_len = payload[cursor]
            if f_len == 0 or cursor + f_len > len(payload): break

            f_desc = payload[cursor + 1]
            f_data = payload[cursor + 2: cursor + f_len]

            # 查找解析規則
            handler = self.__handlers.get((desc_set, f_desc))
            if handler:
                field_res = handler(f_data)
                # --- 優化：在此處自動加入 descriptor 的 Hex 值，方便您核對 ---
                field_res["descriptor"] = hex(f_desc)
                results["fields"].append(field_res)
            else:
                results["fields"].append({"descriptor": hex(f_desc), "raw": f_data.hex()})

            cursor += f_len

        return results

    # --- 各別解析規則 ---

    def _parse_gpio_config(self, data):
        """ 解析 0x0C, 0xC1 (GPIO Configuration) """
        if len(data) >= 4:
            return {
                "type": "GPIO_CONF",
                "pin": data[0],
                "feature": data[1],
                "behavior": data[2],
                "value": data[3]
            }
        return {"type": "GPIO_CONF", "error": "length mismatch"}

    def _parse_ack_nack(self, data):
        """ 解析 0x0C, 0xF1 (ACK/NACK) """
        if len(data) >= 2:
            return {
                "type": "ACK",
                "cmd_echo": hex(data[0]),
                "error_code": data[1]
            }
        return {"type": "ACK", "error": "length mismatch"}