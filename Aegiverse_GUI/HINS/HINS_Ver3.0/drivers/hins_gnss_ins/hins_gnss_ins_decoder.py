# drivers/hins_gnss_ins/hins_gnss_ins_decoder.py
from utils.protocol_manager import ProtocolParser

class HinsGnssInsDecoder(ProtocolParser):
    def push_byte(self, byte):
        self.buffer.append(byte)
        # 狀態 1: 確保 buffer 開頭是 0xFA
        while len(self.buffer) > 0 and self.buffer[0] != 0xFA:
            self.buffer.pop(0)

        # 狀態 2: 需滿 6 bytes 才能解析 V1 Payload 長度
        if len(self.buffer) < 6:
            return None

        # 狀態 3: 解析 V1 Payload 長度 (Byte 4, 5)
        payload_len = self.buffer[4] | (self.buffer[5] << 8)
        total_len = 6 + payload_len + 2

        # 狀態 4: 滿長度後吐出完整 V1 封包
        if len(self.buffer) >= total_len:
            packet = list(self.buffer[:total_len])
            self.buffer = self.buffer[total_len:] # 保留剩餘數據
            return packet
        return None