# drivers/hins_gnss_ins/hins_gnss_ins_reader.py
# -*- coding:UTF-8 -*-
import time
from drivers.base_reader import BaseReader
from utils.protocol_manager import ProtocolDispatcher
from .hins_gnss_ins_decoder import HinsGnssInsDecoder
from .hins_gnss_ins_validator import HinsGnssInsValidator
from .hins_gnss_ins_parser import HinsGnssInsParser

class HinsGnssInsReader(BaseReader):
    def __init__(self, portName="None", baudRate=230400): # 預設波特率建議改為 230400
        super(HinsGnssInsReader, self).__init__(name="HinsGnssIns")
        self.dispatcher = ProtocolDispatcher()
        self.decoder = HinsGnssInsDecoder()
        self.validator = HinsGnssInsValidator()
        self.parser = HinsGnssInsParser()
        self.dispatcher.add_parser(self.decoder, self.handle_packet_flow)

    def run(self):
        self.logger.info(f"{self.device_name} Reader Started.")
        while self.is_run:
            try:
                # 修正：直接使用基類的保護成員 _connector
                if self._connector:
                    available = self._connector.readInputBuffer()
                    if available > 0:
                        raw_data = self._connector.readBinaryList(available)
                        if raw_data:
                            # --- 加入這段來印出 HEX ---
                            hex_str = " ".join([f"{b:02X}" for b in raw_data])
                            print(f"\n[DEBUG RAW] {hex_str}")
                            # -----------------------
                            self.dispatcher.feed_data(raw_data)
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Run loop error: {e}")
                break

    def handle_packet_flow(self, v1_packet):
        """ 剝洋蔥邏輯 """
        if not self.validator.validate(v1_packet):
            return

        v1_type = v1_packet[1]
        v1_cmd = v1_packet[2]
        v1_payload = v1_packet[6:-2]  # 這是剝出來的 MIP 資料 (75 65...)

        # 第一部分: V1 ACK (FA A1)
        if v1_type == 0xA1:
            print(f"[V1 ACK] 指令 {hex(v1_cmd)} 已成功接收")

        elif v1_type == 0xA2:
            if len(v1_payload) > 0:
                # 1. 這是您目前看到的 [RX] 來源 (Hex 原始數據)
                self.raw_ack_qt.emit(v1_payload)

                # 2. 關鍵修正：進入您寫好的 Parser 進行「Descriptor 查表解析」
                parsed_data = self.parser.parse(v1_payload)

                # 3. 為了除錯，直接在這裡印出解析結果
                print(f"[Parser Result] 解析成功: {parsed_data}")

                # 4. 發送解析後的字典訊號 (用於未來更新 UI)
                self.data_ready_qt.emit(parsed_data)
