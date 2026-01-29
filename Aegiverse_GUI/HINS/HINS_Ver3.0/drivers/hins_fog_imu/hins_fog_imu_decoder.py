# drivers/hins_fog_imu/hins_fog_imu_decoder.py
from utils.protocol_manager import ProtocolParser


class HinsFogImuDecoder(ProtocolParser):
    def __init__(self):
        super().__init__()
        # KVH Header: FE 81 FF 55
        self.header = [0xFE, 0x81, 0xFF, 0x55]
        self.packet_len = 64  # Header(4) + Payload(60)

    def push_byte(self, byte):
        self.buffer.append(byte)

        # 狀態 1: 檢查 Buffer 是否足夠長以包含 Header
        while len(self.buffer) >= 4:
            # 檢查 Header 是否匹配
            if (self.buffer[0] == self.header[0] and
                    self.buffer[1] == self.header[1] and
                    self.buffer[2] == self.header[2] and
                    self.buffer[3] == self.header[3]):

                # 狀態 2: Header 匹配，檢查長度是否足夠完整封包
                if len(self.buffer) >= self.packet_len:
                    packet = list(self.buffer[:self.packet_len])
                    self.buffer = self.buffer[self.packet_len:]  # 移除已處理數據
                    return packet  # 吐出完整封包
                else:
                    # 長度不足，等待更多數據
                    return None
            else:
                # Header 不匹配，移出一字元繼續搜尋
                self.buffer.pop(0)

        return None