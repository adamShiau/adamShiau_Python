# drivers/hins_fog_imu/hins_fog_imu_decoder.py
# -*- coding:UTF-8 -*-

# 這裡使用絕對路徑引用，前提是執行環境的 sys.path 包含專案根目錄
from utils.protocol_manager import ProtocolParser


class HinsFogImuDecoder(ProtocolParser):
    """
    HINS FOG IMU 專用解碼器 (Decoder)
    職責：從原始位元組流中精準切出 64 bytes 的固定長度封包
    標頭 (Header): 0xFE, 0x81, 0xFF, 0x55
    """

    def __init__(self):
        super().__init__()
        # 定義此設備特有的同步標頭與封包長度
        self.header = [0xFE, 0x81, 0xFF, 0x55]
        self.packet_len = 64

    def push_byte(self, byte):
        """
        逐位元組輸入的流式解析邏輯 (滑動視窗)
        """
        self.buffer.append(byte)
        h_len = len(self.header)

        # 階段 1: 標頭對齊 (Sync Alignment)
        # 如果目前 buffer 長度還不足以容納標頭，或者不符合標頭前綴，則持續檢查
        if len(self.buffer) <= h_len:
            if self.buffer != self.header[:len(self.buffer)]:
                # 只要對不上標頭，就彈出最前面的位元組，繼續往後找
                self.buffer.pop(0)
            return None

        # 階段 2: 封包收集 (Data Collection)
        # 當標頭對齊後，持續收集直到長度達到預定的 64 bytes
        if len(self.buffer) == self.packet_len:
            # 成功切出一包完整的原始封包 (Raw Packet)
            packet = list(self.buffer)
            self.buffer = []  # 清空緩衝區，準備尋找下一個標頭
            return packet

        return None