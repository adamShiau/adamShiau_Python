# drivers/hins_heading_monitor/hins_monitor_reader.py
from PySide6.QtCore import QObject, Signal
import logging

from .hins_monitor_decoder import HinsMonitorDecoder
from .hins_monitor_validator import HinsMonitorValidator
from .hins_monitor_parser import HinsMonitorParser


class HinsMonitorReader(QObject):
    data_ready_qt = Signal(dict)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("drivers.HinsMonitor.Reader")

        # 組件初始化，遵循統一架構
        self.decoder = HinsMonitorDecoder()
        self.validator = HinsMonitorValidator()
        self.parser = HinsMonitorParser()

        self._connector = None

    def set_connector(self, connector):
        self._connector = connector

    def handle_packet(self, packet):
        """ 接收由總機 (HinsHybridReader) 分發過來的完整封包 """
        # [新增] 印出原始十六進位數據，方便觀察對齊與校驗
        # hex_data = " ".join(f"{b:02X}" for b in packet)
        # self.logger.info(f"RX [MCU_MON]: {hex_data}")

        if self.validator.validate(packet):
            parsed_data = self.parser.parse(packet)
            if parsed_data:
                self.data_ready_qt.emit(parsed_data)