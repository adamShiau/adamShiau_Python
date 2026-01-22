# drivers/hins_fog_imu/hins_fog_imu_reader.py
from PySide6.QtCore import QObject, Signal
import logging
from myLib import common as cmn  # 用於 RCS 矩陣運算
from myLib.crcCalculator import crcLib

# 引入組件
from .hins_fog_imu_decoder import HinsFogImuDecoder
from .hins_fog_imu_parser import HinsFogImuParser


class HinsFogImuReader(QObject):
    # 定義訊號 (跟 BaseReader 一樣，為了相容 UI)
    data_ready_qt = Signal(dict)
    raw_ack_qt = Signal(list)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("drivers.HinsFog")

        # 組件初始化
        self.decoder = HinsFogImuDecoder()
        self.parser = HinsFogImuParser()
        self._connector = None  # 由 HybridReader 注入

        # RCS 設定
        self.is_rcs_mode = False
        self.R_CS = [0, -1, 0, 1, 0, 0, 0, 0, 1]

    def set_connector(self, connector):
        self._connector = connector

    def set_rcs_mode(self, enabled: bool):
        self.is_rcs_mode = enabled

    def handle_packet(self, packet):
        """ 當 Dispatcher 發現 FOG 封包時觸發 """

        # 1. CRC 驗證 (Validator 的角色)
        if crcLib.isCrc32Fail(packet, len(packet)):
            return  # CRC 失敗，丟棄

        # 2. 解析
        parsed_data = self.parser.parse(packet)

        if parsed_data:
            # 3. 業務邏輯：RCS 旋轉 (這就是您希望解耦的地方)
            if self.is_rcs_mode:
                self.apply_rcs_rotation(parsed_data)

            # 4. 發送結果
            self.data_ready_qt.emit(parsed_data)

    def apply_rcs_rotation(self, data):
        """ 內部私有方法：處理旋轉 """
        # 取出原始值
        raw_wx = data["WX"][0];
        raw_wy = data["WY"][0];
        raw_wz = data["WZ"][0]
        raw_ax = data["AX"][0];
        raw_ay = data["AY"][0];
        raw_az = data["AZ"][0]

        # 運算
        r_wx, r_wy, r_wz = cmn._rot_case_to_sensor(raw_wx, raw_wy, raw_wz, self.R_CS)
        r_ax, r_ay, r_az = cmn._rot_case_to_sensor(raw_ax, raw_ay, raw_az, self.R_CS)

        # 寫回
        data["WX"][0] = r_wx;
        data["WY"][0] = r_wy;
        data["WZ"][0] = r_wz
        data["AX"][0] = r_ax;
        data["AY"][0] = r_ay;
        data["AZ"][0] = r_az

    # --- 指令發送區 (封裝 FOG 協議) ---
    def write_fog_cmd(self, cmd, value, fog_ch=3):
        if not self._connector: return
        if value < 0: value = (1 << 32) + value
        payload = [cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF), fog_ch]
        full_cmd = [0xAB, 0xBA] + payload + [0x55, 0x56]
        try:
            self._connector.write(bytearray(full_cmd))
        except:
            pass

    def read_imu(self):
        self.write_fog_cmd(4, 2, 2)

    def stop_imu(self):
        self.write_fog_cmd(4, 4, 2)

    def getVersion(self, mode):
        # 這裡可以保留您原本讀取版本的邏輯
        return "FOG_VER_MOCK"