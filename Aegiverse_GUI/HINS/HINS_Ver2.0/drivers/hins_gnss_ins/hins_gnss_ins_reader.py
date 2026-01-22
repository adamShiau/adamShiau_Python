# drivers/hins_gnss_ins/hins_gnss_ins_reader.py
from PySide6.QtCore import QObject, Signal
import logging

# 引入組件
from .hins_gnss_ins_decoder import HinsGnssInsDecoder
from .hins_gnss_ins_parser import HinsGnssInsParser
from .hins_gnss_ins_validator import HinsGnssInsValidator  # 終於用上它了


class HinsGnssInsReader(QObject):
    data_ready_qt = Signal(dict)
    raw_ack_qt = Signal(list)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("drivers.HinsGnss")

        self.decoder = HinsGnssInsDecoder()
        self.parser = HinsGnssInsParser()
        self.validator = HinsGnssInsValidator()  # 實例化 Validator
        self._connector = None

    def set_connector(self, connector):
        self._connector = connector

    def handle_packet(self, packet):
        """ 當 Dispatcher 發現 GNSS 封包時觸發 """

        # 1. 驗證 (使用 Validator)
        if not self.validator.validate(packet):
            # self.logger.warning("GNSS Packet Validation Failed")
            return

        # 2. 判斷是否為 MIP Data (0xA2)
        v1_type = packet[1]

        # 3. 解析
        # 這裡可以加入更多判斷，只解析感興趣的包
        parsed_data = self.parser.parse(packet)

        if parsed_data:
            # 4. 發送結果
            self.data_ready_qt.emit(parsed_data)

            # 若有需要監看原始 HEX (例如 ACK 封包)
            if v1_type != 0xA2:  # 非數據包通常是 Command Response
                self.raw_ack_qt.emit(packet)

    def write_raw(self, data):
        if self._connector:
            try:
                self._connector.write(bytearray(data))
            except:
                pass