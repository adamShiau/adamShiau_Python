from .mip_types import MIP_CONSTANTS
import struct # 確保有匯入 struct


class ThreeDMSet0x0C:
    def __init__(self):
        # 註冊此 Set 下的 Field Descriptor 處理函式
        self.field_map = {
            0xC1: self._parse_gpio_config,
            0x8F: self._parse_message_format,
            0x85: self._parse_stream_control,
            0x91: self._parse_stream_control,
            0xB3: self._parse_sensor_to_vehicle_dcm,  # 新增 DCM 解析
            0xF1: self._parse_ack_nack,
        }

    def parse_field(self, f_desc, data):
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        # 若無對應 Handler，回傳 Raw Hex
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_sensor_to_vehicle_dcm(self, data):
        """ 解析 0x0C, 0xB3 (DCM Response)  """
        if len(data) < 36:
            return {"type": "SENS_VEH_DCM", "error": "Length mismatch"}

        # 讀取 9 個 float
        values = struct.unpack('>9f', data[:36])
        return {
            "type": "SENS_VEH_DCM",
            "matrix": [values[0:3], values[3:6], values[6:9]]
        }
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
            "pin_mode": MIP_CONSTANTS.PIN_MODE_MAP.get(pin_mode_val, f"UNKNOWN({hex(pin_mode_val)})"),
            # "raw_values": {"feature": hex(feature), "behavior": hex(behavior)},
        }

    def _parse_message_format(self, data):
        """ 解析 0x0C, 0x8F (Message Format Response)  """
        if len(data) < 2: return {"type": "MSG_FORMAT", "error": "Short Data"}
        return {
            "type": "MSG_FORMAT",
            "desc_set": hex(data[0]),
            "num_descriptors": data[1]
        }

    def _parse_stream_control(self, data):
        """ 解析 0x0C, 0x85 (Data Stream Control Response)  """
        # 根據文件，Response Length 為 4
        # Payload 包含: Desc Set (u8), Enabled (bool)
        if len(data) < 2:
            return {"type": "STREAM_CTRL", "error": "Length mismatch"}

        return {
            "type": "STREAM_CTRL",
            "desc_set": hex(data[0]),      # 傳回對應的 Descriptor Set
            "enabled": bool(data[1]),      # 串流是否啟動
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

