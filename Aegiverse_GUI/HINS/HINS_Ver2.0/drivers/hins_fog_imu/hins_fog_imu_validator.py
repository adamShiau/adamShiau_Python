# drivers/hins_fog_imu/hins_fog_imu_validator.py
# -*- coding:UTF-8 -*-
import logging
from myLib.crcCalculator import crcLib  # 沿用舊有 CRC 工具


class HinsFogImuValidator:
    """
    FOG IMU 專用校驗器
    職責：執行 CRC32 檢查，決定是否捨棄封包
    """

    def __init__(self, device_name="HinsFogImu"):
        self.logger = logging.getLogger(f"main.drivers.{device_name}.Validator")
        self.err_count = 0

    def validate(self, packet: list) -> bool:
        """
        返回 True 表示校驗通過，False 則捨棄
        """
        # 使用您原有的 crcLib 檢查
        if crcLib.isCrc32Fail(packet, len(packet)):
            self.err_count += 1
            # 自動記錄 Bug 到 log 中
            self.logger.error(f"CRC Checksum Failed (Total errors: {self.err_count})")
            return False

        return True