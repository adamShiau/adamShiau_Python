# drivers/hins_heading_monitor/hins_monitor_decoder.py
from utils.protocol_manager import ProtocolParser

class HinsMonitorDecoder(ProtocolParser):
    def __init__(self):
        super().__init__()
        # MCU Monitor Header: EB 90
        self.header = [0xEB, 0x90]
        self.packet_len = 36  # 更新後的封包長度

    def push_byte(self, byte):
        self.buffer.append(byte)

        # 搜尋 Header
        while len(self.buffer) >= 2:
            if self.buffer[0] == self.header[0] and self.buffer[1] == self.header[1]:
                # 找到 Header，檢查長度是否足夠
                if len(self.buffer) >= self.packet_len:
                    packet = list(self.buffer[:self.packet_len])
                    self.buffer = self.buffer[self.packet_len:]
                    return packet
                else:
                    return None
            else:
                self.buffer.pop(0)
        return None