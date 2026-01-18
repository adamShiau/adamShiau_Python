# drivers/hins_fog_imu/hins_fog_imu_reader.py
# -*- coding:UTF-8 -*-
import numpy as np
import time
from drivers.base_reader import BaseReader
from utils.protocol_manager import ProtocolDispatcher
from .hins_fog_imu_decoder import HinsFogImuDecoder
from .hins_fog_imu_validator import HinsFogImuValidator
from .hins_fog_imu_parser import HinsFogImuParser

# 定義此設備輸出的資料結構
DATA_STRUCTURE = ["TIME", "WX", "WY", "WZ", "AX", "AY", "AZ",
                  "PD_TEMP_X", "PD_TEMP_Y", "PD_TEMP_Z", "ACC_TEMP", "PITCH", "ROLL", "YAW"]


class HinsFogImuReader(BaseReader):
    def __init__(self, portName="None", baudRate=230400):
        super(HinsFogImuReader, self).__init__(name="HinsFogImu")

        # 實例化各個組件
        self.dispatcher = ProtocolDispatcher()
        self.decoder = HinsFogImuDecoder()
        self.validator = HinsFogImuValidator()
        self.parser = HinsFogImuParser()

        # 註冊解析流程
        self.dispatcher.add_parser(self.decoder, self.handle_packet_flow)

        # 內部累積緩衝區
        self.__temp_batch = {k: np.empty(0) for k in DATA_STRUCTURE}
        self.__packet_count = 0

    def run(self):
        self.logger.info(f"Thread started for {self.device_name}")
        # 注意：這裡假設 self._BaseReader__connector 已透過 set_connector 傳入
        # 為了保證私有變數存取，建議在 BaseReader 使用 self._connector (單底線)

        while self.is_run:
            try:
                available = self._BaseReader__connector.readInputBuffer()
                if available > 0:
                    raw_data = self._BaseReader__connector.readBinaryList(available)
                    self.dispatcher.feed_data(raw_data)
                else:
                    time.sleep(0.001)
            except Exception as e:
                self.logger.critical(f"Runtime Error: {e}")
                self.error_occurred_qt.emit(str(e))
                break

    def handle_packet_flow(self, raw_packet):
        """
        封包處理流水線：Decoder -> Validator -> Parser -> Aggregator
        """
        # 1. 校驗 (Validator)
        if not self.validator.validate(raw_packet):
            return  # 失敗則捨棄，不計入 batch

        # 2. 解析 (Parser)
        data_dict = self.parser.parse(raw_packet)
        if not data_dict:
            return

        # 3. 累積 (Aggregator)
        for k in DATA_STRUCTURE:
            if k in data_dict:
                self.__temp_batch[k] = np.append(self.__temp_batch[k], data_dict[k])

        self.__packet_count += 1

        # 4. 輸出 (達到 batch_size)
        if self.__packet_count >= self.batch_size:
            self.data_ready_qt.emit(self.__temp_batch)
            # 重置
            self.__temp_batch = {k: np.empty(0) for k in DATA_STRUCTURE}
            self.__packet_count = 0