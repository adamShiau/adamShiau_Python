# drivers/hins_gnss_ins/mip_handlers/aiding_set_0x13.py
import struct


class AidingSet0x13:
    def __init__(self):
        # 註冊解析 0x13, 0x81 (Frame Configuration Response)
        self.field_map = {
            0x81: self._parse_frame_config,
            0xF1: self._parse_ack_nack
        }

    def parse_field(self, f_desc, data):
        if isinstance(data, list):
            data = bytes(data)
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _parse_frame_config(self, data):
        # 設備回傳的 data 應該是去除了 1D 81 之後的內容
        # 如果 len(data) 是 27，則 index 如下：
        if len(data) < 27:
            return {"type": "FRAME_CONFIG", "error": "Length mismatch"}

        # data[0] 是 Frame ID, data[1] 是 Format, data[2] 是 Tracking
        frame_id = data[0]
        fmt_val = data[1]
        tracking = bool(data[2])

        # Translation 從 data[3] 開始，共 12 bytes (3個 float)
        trans = struct.unpack('>3f', data[3:15])

        # Rotation 從 data[15] 開始，共 12 bytes (3個 float)
        rot = struct.unpack('>3f', data[15:27])

        return {
            "type": "FRAME_CONFIG",
            "frame_id": frame_id,
            "format": "EULER" if fmt_val == 1 else "QUATERNION",
            "tracking": tracking,
            "translation": list(trans),
            "rotation": list(rot)
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