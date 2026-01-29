# drivers/base_reader.py
# -*- coding:UTF-8 -*-
from PySide6.QtCore import QThread, Signal
import logging

class BaseReader(QThread):
    data_ready_qt = Signal(dict)
    raw_ack_qt = Signal(list)
    finished_qt = Signal()
    error_occurred_qt = Signal(str)

    def __init__(self, name="GenericDevice"):
        super(BaseReader, self).__init__()
        self.device_name = name
        self.logger = logging.getLogger(f"main.drivers.{name}")
        self.__is_run = True
        self._connector = None # 使用單底線，子類別可存取
        self.batch_size = 10

    @property
    def is_run(self):
        return self.__is_run

    @is_run.setter
    def is_run(self, value):
        self.__is_run = value

    def set_connector(self, connector):
        self._connector = connector

    def write_raw(self, data):
        """ 發送原始指令的介面 """
        # 修正：根據 Connector.py，我們直接調用其 write 方法
        if self._connector:
            try:
                self._connector.write(bytearray(data))
                return True
            except Exception as e:
                self.logger.error(f"Write error: {e}")
        return False

    def stop(self):
        self.is_run = False
        self.logger.info(f"[{self.device_name}] Thread stop requested.")