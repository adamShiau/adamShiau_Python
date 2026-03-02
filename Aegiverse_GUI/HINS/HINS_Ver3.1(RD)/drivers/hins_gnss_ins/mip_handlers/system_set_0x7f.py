# drivers/hins_gnss_ins/mip_handlers/system_set_0x7f.py
import struct
from .mip_types import MIP_CONSTANTS

class SystemSet0x7F:
    def __init__(self):
        self.field_map = {
            0x82: self._parse_interface_control,
            0xF1: self._parse_ack_nack,
        }

    def parse_field(self, f_desc, data):
        handler = self.field_map.get(f_desc)
        if handler:
            return handler(data)
        return {"descriptor": hex(f_desc), "raw": data.hex()}

    def _decode_protocols(self, bitfield):
        """ 將 32-bit bitfield 轉為可讀字串 (如: 'MIP, NMEA') """
        active_protocols = []
        for bit, name in MIP_CONSTANTS.PROTOCOL_BITS.items():
            if bitfield & (1 << bit):
                active_protocols.append(name)
        return ", ".join(active_protocols) if active_protocols else "None"

    def _parse_interface_control(self, data):
        """ 解析 0x7F, 0x82 (Interface Control Response)  """
        if len(data) < 9:
            return {"type": "INTERFACE_CTRL", "error": "Length < 9"}

        port_id = data[0]
        # 解包為 Unsigned 32-bit (Big Endian)
        in_proto_val = struct.unpack('>I', bytes(data[1:5]))[0]
        out_proto_val = struct.unpack('>I', bytes(data[5:9]))[0]

        return {
            "type": "INTERFACE_CTRL",
            "port": MIP_CONSTANTS.PORT_MAP.get(port_id, f"Unknown({port_id})"), # 轉換 Port
            "incoming": self._decode_protocols(in_proto_val), # 轉換 Protocol [cite: 24]
            "outgoing": self._decode_protocols(out_proto_val)
        }

    def _parse_ack_nack(self, data):
        return {
            "type": "ACK",
            "cmd_echo": hex(data[0]),
            "error_code": data[1],
            "status": "OK" if data[1] == 0x00 else "ERROR"
        }