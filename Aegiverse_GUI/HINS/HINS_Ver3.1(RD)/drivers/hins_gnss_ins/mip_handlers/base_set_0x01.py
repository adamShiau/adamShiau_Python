# drivers/hins_gnss_ins/mip_handlers/base_set_0x01.py
import struct


class BaseSet0x01:
    def __init__(self):
        self.field_map = {
            # 根據 PDF，Comm Port Speed (0x09) 的 Response Descriptor 是 0x89
            0x89: self._parse_comm_speed,
            0xF1: self._parse_ack_nack,  # Base Set 的 ACK
        }

    def parse_field(self, f_desc, data):
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_comm_speed(self, data):
        """ 解析 0x01, 0x09 (Comm Port Speed) 回傳的 0x89 """
        # 格式: Port(1 byte) + BaudRate(4 bytes, u32) = 5 bytes
        if len(data) < 5:
            return {"type": "BAUD_RATE", "error": "Length < 5"}

        port_id = data[0]
        target_data = bytes(data[1:5])
        baud_rate = struct.unpack('>I', target_data)[0]

        return {
            "type": "BAUD_RATE",  # 修正：對應 UI 的判斷字串
            "port_id": port_id,
            "baud_rate": baud_rate
        }

    def _parse_ack_nack(self, data):
        if len(data) < 2:
            return {"type": "ACK", "error": "Length mismatch"}

        return {
            "type": "ACK",
            "cmd_echo": hex(data[0]),
            "error_code": data[1],
            "status": "OK" if data[1] == 0x00 else "ERROR"
        }