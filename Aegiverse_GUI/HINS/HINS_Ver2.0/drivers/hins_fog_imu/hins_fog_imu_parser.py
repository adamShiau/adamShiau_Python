# drivers/hins_fog_imu/hins_fog_imu_parser.py
import struct
import numpy as np
# 引用您舊有的庫
from myLib import common as cmn


class HinsFogImuParser:
    def __init__(self):
        # 定義輸出的資料結構 Keys (對齊 UI 需求)
        self.keys = ["TIME", "WX", "WY", "WZ", "AX", "AY", "AZ",
                     "PD_TEMP_X", "PD_TEMP_Y", "PD_TEMP_Z", "ACC_TEMP",
                     "PITCH", "ROLL", "YAW"]

    def parse(self, raw_packet: list) -> dict:
        """
        輸入: 包含 Header 的 64 bytes list
        輸出: UI 需要的 dict (numpy array 格式以相容舊 UI)
        """
        if len(raw_packet) != 64:
            return {}

        # 呼叫舊有的 common.py 進行解析 (Header 佔 4 bytes)
        # 根據 pigImuReader，這裡使用 IRIS_AHRS_Rotate
        # 注意：這裡暫時不處理 R_CS 旋轉，若需旋轉可在 Reader 層傳入參數
        try:
            results = cmn.IRIS_AHRS_Rotate(
                raw_packet,
                EN=1,
                POS_TIME=4,  # Header 4 bytes
                sf_a=1,
                sf_b=0,
                PRINT=0
            )

            # results tuple 順序:
            # fpga_time, wx, wy, wz, ax, ay, az,
            # temp1, temp2, temp3, acc_temp,
            # pitch, roll, yaw

            # 轉成 Dictionary，並包裝成 numpy array (因為 pigImuWidget 畫圖需要)
            data_dict = {
                "TIME": np.array([results[0]]),
                "WX": np.array([results[1]]),
                "WY": np.array([results[2]]),
                "WZ": np.array([results[3]]),
                "AX": np.array([results[4]]),
                "AY": np.array([results[5]]),
                "AZ": np.array([results[6]]),
                "PD_TEMP_X": np.array([results[7]]),  # Temp1
                "PD_TEMP_Y": np.array([results[8]]),  # Temp2
                "PD_TEMP_Z": np.array([results[9]]),  # Temp3
                "ACC_TEMP": np.array([results[10]]),
                "PITCH": np.array([results[11]]),
                "ROLL": np.array([results[12]]),
                "YAW": np.array([results[13]])
            }
            return data_dict

        except Exception as e:
            print(f"Parser Error: {e}")
            return {}