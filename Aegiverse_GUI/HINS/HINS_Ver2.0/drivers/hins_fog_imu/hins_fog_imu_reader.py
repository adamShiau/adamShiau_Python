# drivers/hins_fog_imu/hins_fog_imu_reader.py
import time
import logging
from drivers.base_reader import BaseReader
from utils.protocol_manager import ProtocolDispatcher
from .hins_fog_imu_decoder import HinsFogImuDecoder
from .hins_fog_imu_parser import HinsFogImuParser

# 引用舊有 CRC 庫
from myLib.crcCalculator import crcLib


class HinsFogImuReader(BaseReader):
    def __init__(self):
        super().__init__(name="HinsFogImu")
        self.dispatcher = ProtocolDispatcher()
        self.decoder = HinsFogImuDecoder()
        self.parser = HinsFogImuParser()

        # 將 Decoder 綁定到 Callback
        self.dispatcher.add_parser(self.decoder, self.handle_packet)

    def run(self):
        self.logger.info("HinsFogImu Reader Started.")
        while self.is_run:
            try:
                if self._connector:
                    available = self._connector.readInputBuffer()
                    if available > 0:
                        raw_data = self._connector.readBinaryList(available)
                        if raw_data:
                            self.dispatcher.feed_data(raw_data)
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Run loop error: {e}")
                break

    def handle_packet(self, packet):
        """ 當 Decoder 抓到完整 64 bytes 封包時觸發 """

        # 1. CRC 檢查 (使用舊有的 crcLib)
        # packet 是 list，crcLib 可能需要 list 或 bytes，根據舊 code 傳 list 即可
        if crcLib.isCrc32Fail(packet, len(packet)):
            self.logger.warning("CRC32 Check Failed")
            return

        # 2. 發送原始數據訊號 (可供 Debug)
        self.raw_ack_qt.emit(packet)

        # 3. 解析物理量
        parsed_data = self.parser.parse(packet)

        # 4. 發送給 UI 畫圖
        if parsed_data:
            self.data_ready_qt.emit(parsed_data)

    def write_fog_cmd(self, cmd, value, fog_ch=3):
        """ 移植舊的 writeImuCmd """
        if value < 0:
            value = (1 << 32) + value

        # 建構 Payload
        payload = [cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF), fog_ch]

        # 加上 Header (AB BA) 與 Tail (55 56)
        full_cmd = [0xAB, 0xBA] + payload + [0x55, 0x56]

        self.write_raw(full_cmd)
        self.logger.info(f"Sent FOG Cmd: {cmd}, Val: {value}")

    def read_imu(self):
        """ 啟動連續讀取 (Cmd 4, Val 2) """
        self.logger.info("Start Reading IMU...")
        if self._connector: self._connector.flushInputBuffer()
        self.write_fog_cmd(4, 2, 2)

    def stop_imu(self):
        """ 停止讀取 (Cmd 4, Val 4) """
        self.logger.info("Stop Reading IMU...")
        self.write_fog_cmd(4, 4, 2)
        if self._connector: self._connector.flushInputBuffer()