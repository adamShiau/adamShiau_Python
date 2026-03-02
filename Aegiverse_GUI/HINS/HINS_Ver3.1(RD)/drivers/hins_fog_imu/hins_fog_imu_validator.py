# drivers/hins_fog_imu/hins_fog_imu_validator.py
from myLib.crcCalculator import crcLib
import logging

class HinsFogImuValidator:
    def __init__(self):
        self.logger = logging.getLogger("drivers.HinsFog.Validator")

    def validate(self, packet: list) -> bool:
        """
        驗證 FOG 封包的完整性 (CRC32)
        """
        if not packet:
            return False

        # FOG 使用 CRC32 校驗
        # isCrc32Fail 回傳 True 代表校驗失敗 (Fail)
        if crcLib.isCrc32Fail(packet, len(packet)):
            # 您可以選擇開啟 log，但在 Hybrid 模式下可能會誤報 GNSS 封包
            # self.logger.warning(f"CRC32 Check Failed. Len: {len(packet)}")
            return False

        return True