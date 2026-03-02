# drivers/hins_hybrid_reader.py
# -*- coding:UTF-8 -*-
import time
from drivers.base_reader import BaseReader
from utils.protocol_manager import ProtocolDispatcher


class HinsHybridReader(BaseReader):
    def __init__(self):
        super().__init__(name="HinsHybrid")
        self.dispatcher = ProtocolDispatcher()
        self.sub_readers = []  # 用來管理子設備

    def add_device(self, device_reader):
        """ 註冊子設備 (FogReader, GnssReader) """
        self.sub_readers.append(device_reader)

        # 1. 將子設備的 Decoder 註冊到分發器
        #    當 Decoder 湊齊封包時，會自動呼叫 device_reader.handle_packet
        self.dispatcher.add_parser(device_reader.decoder, device_reader.handle_packet)

        # 2. 讓子設備能共用 Connector (為了發送指令 write_raw)
        device_reader.set_connector(self._connector)

    def set_connector(self, connector):
        """ 覆寫父類別方法，確保子設備也能拿到 connector """
        super().set_connector(connector)
        for reader in self.sub_readers:
            reader.set_connector(connector)

    def run(self):
        self.logger.info("Hybrid Reader (Dispatcher) Started.")
        while self.is_run:
            try:
                if self._connector:
                    available = self._connector.readInputBuffer()
                    if available > 0:
                        raw_data = self._connector.readBinaryList(available)
                        if raw_data:
                            # [唯一職責]：餵資料給分發器
                            self.dispatcher.feed_data(raw_data)
                    else:
                        time.sleep(0.001)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Run loop error: {e}")
                break

    def flush_buffers(self):
        if self._connector:
            try:
                self._connector.flushInputBuffer()
            except:
                pass
        # 通知所有子設備清空自己的 Decoder Buffer
        for reader in self.sub_readers:
            reader.decoder.buffer = []