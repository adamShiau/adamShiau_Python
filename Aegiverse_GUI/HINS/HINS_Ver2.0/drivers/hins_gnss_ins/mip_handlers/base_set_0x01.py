# drivers/hins_gnss_ins/mip_handlers/base_set_0x01.py
import struct


class BaseSet0x01:
    def __init__(self):
        self.field_map = {
            # --- 修正處：必須對應回傳的 Descriptor 0x89 ---
            0x89: self._parse_comm_speed,  # Comm Port Speed (0x09 的回傳是 0x89)
            0xF1: self._parse_ack_nack,  # Base Set 也有 ACK
        }

    def parse_field(self, f_desc, data):
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_comm_speed(self, data):
        """ 解析 0x01, 0x09 (Comm Port Speed) 回傳的 0x89 """
        # 格式: Port(1) + BaudRate(4) = 5 bytes
        if len(data) < 5:
            return {"type": "COMM_SPEED", "error": "Length < 5"}

        port_id = data[0]
        # 解包 U32 (Big Endian)
        baud_rate = struct.unpack('>I', data[1:5])[0]

        return {
            "type": "COMM_SPEED",
            "port_id": port_id,
            "baud_rate": baud_rate
        }

    def _parse_ack_nack(self, data):
        return {
            "type": "ACK",
            "cmd_echo": hex(data[0]),
            "error_code": data[1],
            "status": "OK" if data[1] == 0x00 else "ERROR"
        }