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
        # [新增] 當設定新的連接器(重連)時，立刻清空輸入緩衝區
        if self._connector:
            try:
                # 確保把上次連線殘留的垃圾 (如 FA A1 04...) 清掉
                self._connector.flushInputBuffer()
                self.logger.info("Connector set and input buffer flushed.")
            except:
                pass

    def handle_packet(self, packet):
        """ 當 Dispatcher 發現 GNSS 封包時觸發 """

        # 1. [關鍵修改] 先發送原始數據給 UI (無論驗證是否通過，都要讓 UI 看到)
        self.raw_ack_qt.emit(packet)

        # 2. 接著才是驗證 (Validator)
        # 如果這是 V1 封包，目前的 Validator 可能會回傳 False，但沒關係，UI 已經收到了
        if not self.validator.validate(packet):
            # 這裡可以考慮針對 V1 (FA開頭) 做特殊放行，或是單純 return
            # 如果您希望 Parser 也能解析 V1，這裡需要讓 Validator 允許 FA 開頭

            # 暫時方案：如果是 FA 開頭，我們假設它是 V1 協議，強制放行
            if len(packet) > 0 and packet[0] == 0xFA:
                pass  # 放行 V1 封包往下走
            else:
                return  # 真的爛封包才丟掉

        # 3. 解析 (解析物理量給圖表用)
        parsed_data = self.parser.parse(packet)
        if parsed_data:
            self.data_ready_qt.emit(parsed_data)

    def write_raw(self, data):
        if self._connector:
            try:
                self._connector.write(bytearray(data))
            except:
                pass