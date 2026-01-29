# drivers/hins_fog_imu/hins_fog_imu_reader.py
from PySide6.QtCore import QObject, Signal
import logging
import time
from myLib import common as cmn

# 引入組件
from .hins_fog_imu_validator import HinsFogImuValidator
from .hins_fog_imu_decoder import HinsFogImuDecoder
from .hins_fog_imu_parser import HinsFogImuParser


class HinsFogImuReader(QObject):
    data_ready_qt = Signal(dict)
    raw_ack_qt = Signal(list)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("drivers.HinsFog")

        # 組件初始化
        self.decoder = HinsFogImuDecoder()
        self.parser = HinsFogImuParser()
        self.validator = HinsFogImuValidator()

        self._connector = None

        # RCS 設定
        self.is_rcs_mode = False
        self.R_CS = [0, -1, 0, 1, 0, 0, 0, 0, 1]

    def set_connector(self, connector):
        self._connector = connector

    def set_rcs_mode(self, enabled: bool):
        self.is_rcs_mode = enabled
        self.logger.info(f"RCS Mode: {enabled}")

    def handle_packet(self, packet):
        # 1. CRC 驗證
        if not self.validator.validate(packet):
            return  # 驗證失敗 (CRC 錯誤或非 FOG 封包)，直接丟棄

            # 2. 解析
        parsed_data = self.parser.parse(packet)

        if parsed_data:
            # 3. RCS 旋轉
            if self.is_rcs_mode:
                self.apply_rcs_rotation(parsed_data)

            # 4. 發送結果
            self.data_ready_qt.emit(parsed_data)

    def apply_rcs_rotation(self, data):
        try:
            raw_wx = data["WX"][0];
            raw_wy = data["WY"][0];
            raw_wz = data["WZ"][0]
            raw_ax = data["AX"][0];
            raw_ay = data["AY"][0];
            raw_az = data["AZ"][0]
            r_wx, r_wy, r_wz = cmn._rot_case_to_sensor(raw_wx, raw_wy, raw_wz, self.R_CS)
            r_ax, r_ay, r_az = cmn._rot_case_to_sensor(raw_ax, raw_ay, raw_az, self.R_CS)
            data["WX"][0] = r_wx;
            data["WY"][0] = r_wy;
            data["WZ"][0] = r_wz
            data["AX"][0] = r_ax;
            data["AY"][0] = r_ay;
            data["AZ"][0] = r_az
        except Exception as e:
            self.logger.error(f"RCS Calculation Error: {e}")

    # --- [核心修復] 相容性介面 & 真實功能轉發 ---

    def flushInputBuffer(self, debug_info=""):
        if self._connector:
            try:
                self._connector.flushInputBuffer()
            except:
                pass

    def writeImuCmd(self, cmd, value, ch=6):
        """ 舊 UI 呼叫此方法發送指令 """
        self.write_fog_cmd(cmd, value, ch)

    def readInputBuffer(self):
        if self._connector:
            return self._connector.readInputBuffer()
        return 0

    def readBinaryList(self, num):
        if self._connector:
            return self._connector.readBinaryList(num)
        return []

    # --- [關鍵] 直接轉發 Connector 實作的 Dump 方法 ---
    # 根據您提供的 pigImuReader.py，這些邏輯其實都在 Connector 裡

    def dump_SN_parameters(self, ch):
        if self._connector:
            return self._connector.dump_SN_parameters(ch)
        return 0

    def dump_fog_parameters(self, ch):
        if self._connector:
            return self._connector.dump_fog_parameters(ch)
        return {}

    def dump_cali_parameters(self, ch):
        if self._connector:
            return self._connector.dump_cali_parameters(ch)
        return {}

    def dump_configuration(self):
        if self._connector:
            return self._connector.dump_configuration()
        return {}

    def getVersion(self, ch):
        if self._connector:
            return self._connector.getVersion(ch)
        return "Unknown"

    def update_SN_parameters(self, para):
        """
        相容介面: 寫入產品序號 (SN) 到設備
        邏輯移植自 pigImuReader.py
        Args:
            para (list): 已經轉換好的 Byte List (不包含 header/tail)
        """
        if not self._connector:
            return "錯誤：未連接設備"

        try:
            # 根據舊代碼，需要在開頭插入 0x6E
            # 注意：這裡使用 insert 會修改傳入的 list，這跟舊邏輯一致
            para.insert(0, 0x6E)

            # Header: CD DC
            self._connector.write(bytearray([0xCD, 0xDC]))
            # Payload
            self._connector.write(bytearray(para))
            # Tail: 57 58
            self._connector.write(bytearray([0x57, 0x58]))

            # 加入一點延遲確保寫入完成
            time.sleep(0.1)

            return "已將輸入內容寫入設備"  # 回傳成功訊息給 UI

        except Exception as e:
            self.logger.error(f"Update SN Error: {e}")
            return f"寫入失敗: {e}"

    # --- FOG 協議封裝 (Write Protocol) ---
    # 參考 pigImuReader.py 的 writeImuCmd 實作

    def write_fog_cmd(self, cmd, value, fog_ch=3):
        if not self._connector: return

        # 負數處理
        if value < 0: value = (1 << 32) + value

        # Payload: [CMD, Val3, Val2, Val1, Val0, CH]
        payload = [cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF), fog_ch]

        try:
            # Header: AB BA
            self._connector.write(bytearray([0xAB, 0xBA]))
            # Payload
            self._connector.write(bytearray(payload))
            # Tail: 55 56
            self._connector.write(bytearray([0x55, 0x56]))

            # 舊版有加 delay，這裡建議也加上以保安全
            cmn.wait_ms(150)
        except:
            pass

    def read_imu(self):
        self.flushInputBuffer("read_start")
        self.write_fog_cmd(5, 2, 2)

    def stop_imu(self):
        self.write_fog_cmd(5, 4, 2)
        self.flushInputBuffer("stop")