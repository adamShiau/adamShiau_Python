from .mip_types import MIP_CONSTANTS


class SystemSet0x0C:
    def __init__(self):
        # 註冊此 Set 下的 Field Descriptor 處理函式
        self.field_map = {
            0xC1: self._parse_gpio_config,  # GPIO Config Response (0x41 -> 0xC1)
            0xF1: self._parse_ack_nack,  # ACK/NACK Field
        }

    def parse_field(self, f_desc, data):
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        # 若無對應 Handler，回傳 Raw Hex
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_gpio_config(self, data):
        """ 解析 0x0C, 0xC1 (GPIO Configuration) """
        if len(data) < 4:
            return {"type": "GPIO_CONF", "error": "Length < 4"}

        pin = data[0]
        feature = data[1]
        behavior = data[2]
        pin_mode_val = data[3]

        return {
            "type": "GPIO_CONF",
            "pin_id": pin,
            "feature": MIP_CONSTANTS.FEATURE_MAP.get(feature, f"UNKNOWN({hex(feature)})"),
            "behavior": MIP_CONSTANTS.BEHAVIOR_MAP.get(behavior, f"UNKNOWN({hex(behavior)})"),
            "pin_state": MIP_CONSTANTS.PIN_MODE_MAP.get(pin_mode_val, f"UNKNOWN({hex(pin_mode_val)})"),
            "raw_values": {"feature": hex(feature), "behavior": hex(behavior)},
            "raw_pin_mode": pin_mode_val
        }

    def _parse_ack_nack(self, data):
        """ 解析 0x0C, 0xF1 (ACK/NACK) """
        if len(data) < 2:
            return {"type": "ACK", "error": "Length mismatch"}

        return {
            "type": "ACK",
            "cmd_echo": hex(data[0]),
            "error_code": data[1],
            "status": "OK" if data[1] == 0x00 else "ERROR"
        }