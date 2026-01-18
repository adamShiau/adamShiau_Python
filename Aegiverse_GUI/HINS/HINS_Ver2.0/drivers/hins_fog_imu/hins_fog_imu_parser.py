# drivers/hins_fog_imu/hins_fog_imu_parser.py
# -*- coding:UTF-8 -*-
import logging
from myLib import common as cmn # 沿用您原本的數學轉換庫

class HinsFogImuParser:
    """
    FOG IMU 專用解析器
    職責：將 64 bytes 封包轉換為物理量字典
    """
    def __init__(self, device_name="HinsFogImu"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Parser")
        # 這裡可以預留座標旋轉矩陣或標定參數
        self.sf_a = 1
        self.sf_b = 0

    def parse(self, packet: list) -> dict:
        """
        將原始列表轉換為物理量字典
        """
        try:
            # 調用您原本 common.py 中的 IRIS_AHRS_Rotate
            # POS_TIME=4 是因為 Header 佔了 4 bytes (0xFE 0x81 0xFF 0x55)
            data_dict = cmn.IRIS_AHRS_Rotate(
                packet,
                EN=1,
                PRINT=0,
                sf_a=self.sf_a,
                sf_b=self.sf_b,
                POS_TIME=4,
                use_rcs=False # 這裡可依需求調整是否使用座標轉換
            )
            return data_dict
        except Exception as e:
            self.logger.error(f"Parse Error: {e}")
            return None