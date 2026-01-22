# drivers/hins_hybrid_reader.py
# -*- coding:UTF-8 -*-
import time
from drivers.base_reader import BaseReader
from utils.protocol_manager import ProtocolDispatcher

# 引入 FOG 相關組件
from drivers.hins_fog_imu.hins_fog_imu_decoder import HinsFogImuDecoder
from drivers.hins_fog_imu.hins_fog_imu_parser import HinsFogImuParser
from myLib.crcCalculator import crcLib

# 引入 GNSS 相關組件
from drivers.hins_gnss_ins.hins_gnss_ins_decoder import HinsGnssInsDecoder
from drivers.hins_gnss_ins.hins_gnss_ins_validator import HinsGnssInsValidator
from drivers.hins_gnss_ins.hins_gnss_ins_parser import HinsGnssInsParser


class HinsHybridReader(BaseReader):
    def __init__(self):
        super().__init__(name="HinsHybrid")

        self.dispatcher = ProtocolDispatcher()

        # --- 1. 初始化 FOG 組件 ---
        self.fog_decoder = HinsFogImuDecoder()
        self.fog_parser = HinsFogImuParser()
        # 註冊 FOG 解碼器
        self.dispatcher.add_parser(self.fog_decoder, self.handle_fog_packet)

        # --- 2. 初始化 GNSS 組件 ---
        self.gnss_decoder = HinsGnssInsDecoder()
        self.gnss_validator = HinsGnssInsValidator()
        self.gnss_parser = HinsGnssInsParser()
        # 註冊 GNSS 解碼器
        self.dispatcher.add_parser(self.gnss_decoder, self.handle_gnss_packet)

    def run(self):
        self.logger.info("HinsHybrid Reader Started.")
        while self.is_run:
            try:
                if self._connector:
                    available = self._connector.readInputBuffer()
                    if available > 0:
                        raw_data = self._connector.readBinaryList(available)
                        if raw_data:
                            # [關鍵]：讀一次，ProtocolDispatcher 會自動餵給所有註冊的 Decoder
                            # 這就是您要的 "把數值丟給設備的 decoder buffer"
                            self.dispatcher.feed_data(raw_data)
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Run loop error: {e}")
                break

    # --- FOG 處理邏輯 ---
    def handle_fog_packet(self, packet):
        # CRC 檢查
        if crcLib.isCrc32Fail(packet, len(packet)):
            return

        # 解析物理量
        parsed_data = self.fog_parser.parse(packet)
        if parsed_data:
            self.data_ready_qt.emit(parsed_data)  # 發送給 UI 畫圖

    # --- GNSS 處理邏輯 ---
    def handle_gnss_packet(self, packet):
        # 驗證 checksum
        if not self.gnss_validator.validate(packet):
            return

        # 剝殼
        v1_type = packet[1]
        v1_cmd = packet[2]

        if v1_type == 0xA2:  # MIP Data
            mip_payload = packet[6:-2]
            if len(mip_payload) > 0:
                parsed_data = self.gnss_parser.parse(packet)  # 傳入完整封包讓 Parser 處理 Header
                if parsed_data:
                    self.data_ready_qt.emit(parsed_data)  # 發送給 Config Widget

    # --- FOG 指令封裝 (從舊 Reader 搬過來) ---
    def write_fog_cmd(self, cmd, value, fog_ch=3):
        if value < 0: value = (1 << 32) + value
        payload = [cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF), fog_ch]
        full_cmd = [0xAB, 0xBA] + payload + [0x55, 0x56]
        self.write_raw(full_cmd)

    def read_imu(self):
        self.write_fog_cmd(4, 2, 2)

    def stop_imu(self):
        self.write_fog_cmd(4, 4, 2)