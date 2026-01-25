# drivers/hins_gnss_ins/mip_handlers/filter_set_0x0d.py
import struct


class FilterSet0x0D:
    def __init__(self):
        # 註冊解析 0x0D, 0xD4 (Antenna Offset Response)
        self.field_map = {
            0xD4: self._parse_antenna_offset,
            0xD0: self._parse_aiding_control,
            0xF1: self._parse_ack_nack
        }

    def parse_field(self, f_desc, data):
        # --- 新增：確保 data 為 bytes 格式 ---
        if isinstance(data, list):
            data = bytes(data)

        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)

        # 若無對應 Handler，現在 data.hex() 不會報錯了
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_antenna_offset(self, data):
        """ 解析 0x0D, 0xD4 數據 (Receiver ID + Vector3f)  """
        # 二次確保格式 (防禦性編程)
        if isinstance(data, list):
            data = bytes(data)

        # 數據長度應為 13 bytes (Receiver ID u8 + Vector3f 12 bytes)
        if len(data) < 13:
            return {"type": "ANTENNA_OFFSET", "error": "Length mismatch"}

        receiver_id = data[0]
        # Vector3f 為 3 個 float (12 bytes)
        offset = struct.unpack('>3f', data[1:13])

        return {
            "type": "ANTENNA_OFFSET",
            "receiver_id": receiver_id,
            "offset": list(offset)
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

    def _parse_aiding_control(self, data):
        """ 解析 0x0D, 0xD0 數據 (Aiding Source u16 + Enable bool)  """
        if len(data) < 3:
            return {"type": "AIDING_CONTROL", "error": "Length mismatch"}

        # Aiding Source 為 u16 (2 bytes), Enable 為 bool (1 byte)
        source_val = struct.unpack('>H', data[0:2])[0]
        enabled = bool(data[2])

        # 映射表，對應 EXTERNAL_HEADING 為 5
        source_map = {
            0: "GNSS_POS_VEL",
            1: "GNSS_HEADING",
            5: "EXTERNAL_HEADING",
            # ... 其他可根據需求擴充
        }

        return {
            "type": "AIDING_CONTROL",
            "source": source_map.get(source_val, f"UNKNOWN({source_val})"),
            "enabled": enabled
        }
