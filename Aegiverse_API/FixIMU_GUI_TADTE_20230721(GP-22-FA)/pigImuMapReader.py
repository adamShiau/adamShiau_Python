""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import time
from datetime import datetime

from PyQt5.QtWidgets import QApplication

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from myLib.myKM.main import Driving



IMU_DATA_STRUCTURE = {
    "One_TIME": np.zeros(1),
    "One_WX": np.zeros(1),
    "One_WY": np.zeros(1),
    "One_WZ": np.zeros(1),
    "One_AX": np.zeros(1),
    "One_AY": np.zeros(1),
    "One_AZ": np.zeros(1),
    "One_PD_TEMP": np.zeros(1),
    "One_latitude(deg)": np.zeros(1),
    "One_longitude(deg)": np.zeros(1)
}

Integration_DATA_STRUCTURE = {
    "One_TIME": np.zeros(1),
    "One_WX": np.zeros(1),
    "One_WY": np.zeros(1),
    "One_WZ": np.zeros(1),
    "One_AX": np.zeros(1),
    "One_AY": np.zeros(1),
    "One_AZ": np.zeros(1),
    "One_PD_TEMP_X": np.zeros(1),
    "One_PD_TEMP_Y": np.zeros(1),
    "One_PD_TEMP_Z": np.zeros(1),
    "One_latitude(deg)": np.zeros(1),
    "One_longitude(deg)": np.zeros(1),
    "GPS": np.zeros(1),
    "GLONASS": np.zeros(1),
    "BeiDou": np.zeros(1),
    "VBOXTime": np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1),
    "Velocity": np.zeros(1),
    'Heading': np.zeros(1),
    'Altitude': np.zeros(1),
    'Vertical_Vel': np.zeros(1),
    "Pitch_KF": np.zeros(1),
    "Roll_KF": np.zeros(1),
    "Heading_KF": np.zeros(1),
    "Pitch_rate": np.zeros(1),
    "Roll_rate": np.zeros(1),
    "Yaw_rate": np.zeros(1),
    "Acc_X": np.zeros(1),
    "Acc_Y": np.zeros(1),
    "Acc_Z": np.zeros(1),
    "Date": np.zeros(1),
    "KF_Status": np.zeros(1),
    "Pos_Quality": np.zeros(1),
    'Vel_Quality': np.zeros(1),
    "Heading2_KF": np.zeros(1),
    "kvh_wx": np.zeros(1),
    "kvh_wy": np.zeros(1),
    "kvh_wz": np.zeros(1),
    "kvh_ax": np.zeros(1),
    "kvh_ay": np.zeros(1),
    "kvh_az": np.zeros(1),
    "kvh_status": np.zeros(1),
    'kvh_seq_num': np.zeros(1),
    'kvh_Temperature': np.zeros(1)
}

class pigImuMapReader(QThread):
    if not __name__ == "__main__":
        # 即時軌跡
        realTImePointqt_signal = pyqtSignal(object, object, object)
        timePointData_signal = pyqtSignal(object)

    def __init__(self):
        super(pigImuMapReader, self).__init__()
        self.initKM = Driving()
        self.__realTMArr = []
        self.__realTM = []
        self.__vbox_marker = []
        self.__integration = {k: np.empty(0) for k in set(Integration_DATA_STRUCTURE)}
        self.lat = 25.0207716 + 0.00000011
        self.long = 121.22212 + 0.00000012

    def RealTimeTrackStart(self, RealTimeTrackDataArray, VB, KVHRowData):
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        latiLongi = []
        # realTM = np.array([])
        self.initTime = True
        self.__integration = {k: np.empty(0) for k in set(Integration_DATA_STRUCTURE)}
        #self.__mapVal, self.__turnAng = self.ConvertToMapValue(RealTimeTrackDataArray, VB)
        self.Integration_Data(RealTimeTrackDataArray, VB, KVHRowData)
        # self.__realTMArr.append(self.__mapVal[-1].tolist())
        # if self.initTime:
        #     dmax = 0.000001
        #     inti_Point = self.__realTMArr[0]
        #     self.initTime = False
        # if len(self.__realTM) > 1000:
        #     self.__realTM.append(self.__mapVal[-1].tolist())
        #     self.__realTM = self.__realTM[1:]
        #     # self.realTM = []
        #     # for k in range(len(self.realTMArr)):
        #     #     if k == 0:
        #     #         self.realTM.append(self.realTMArr[k])
        #     #     if k != 0 and k != (len(self.realTMArr) - 1):
        #     #         ABPointLine = ((self.realTMArr[-1][0] - inti_Point[0]) ** 2 + (
        #     #                     self.realTMArr[-1][1] - inti_Point[1]) ** 2) ** 0.5  # 起終的連線長度
        #     #         CAToCB_Dot_product = (inti_Point[0] - self.realTMArr[k][0]) * (self.realTMArr[-1][0] - self.realTMArr[k][0]) + (
        #     #                 inti_Point[1] - self.realTMArr[k][1]) * (self.realTMArr[-1][1] - self.realTMArr[k][1])
        #     #
        #     #         CD_Distance = abs(CAToCB_Dot_product) / ABPointLine
        #     #
        #     #         if (CD_Distance > dmax):
        #     #             inti_Point = self.realTMArr[k]
        #     #             self.realTM.append(self.realTMArr[k])
        #     #
        #     #         # else:
        #     #         #     del self.realTMArr[k]
        #
        # else:
        #     self.__realTM.append(self.__mapVal[-1].tolist())


        if len(self.__vbox_marker) > 1000:
            self.__vbox_marker.append([VB["Latitude"][-1], VB["Longitude"][-1]])
            # self.lat = self.lat + 0.000005
            # self.long = self.long + 0.000002
            # self.__vbox_marker.append([self.lat, self.long])
            self.__vbox_marker = self.__vbox_marker[1:]
        else:
            self.__vbox_marker.append([VB["Latitude"][-1], VB["Longitude"][-1]])
            # self.lat = self.lat + 0.000005
            # self.long = self.long + 0.000002
            # self.__vbox_marker.append([self.lat, self.long])

        # print("VBOX的值:")
        # print(self.__vbox_marker)

        # if not __name__ == "__main__":
        #     self.realTImePointqt_signal.emit(self.__realTM, self.__turnAng, self.__vbox_marker)


        # end of while loop

    # End of memsImuReader::run


    def Integration_Data(self, imudata, VB_data, KVHRowData):
        self.__integration = {k: np.empty(0) for k in set(Integration_DATA_STRUCTURE)}
        DataNameList = ["One_TIME", "One_WX", "One_WY", "One_WZ", "One_AX", "One_AY", "One_AZ", "One_PD_TEMP_X", "One_PD_TEMP_Y", "One_PD_TEMP_Z", "One_latitude(deg)", "One_longitude(deg)", "GPS",
                        "GLONASS", "BeiDou", "VBOXTime", "Latitude",  "Longitude",  "Velocity",  'Heading',  'Altitude',  'Vertical_Vel',  "Pitch_KF",  "Roll_KF",  "Heading_KF",
                        "Pitch_rate",  "Roll_rate",  "Yaw_rate",  "Acc_X",  "Acc_Y",  "Acc_Z",  "Date",  "KF_Status",  "Pos_Quality",  'Vel_Quality',  "Heading2_KF",
                        "kvh_wx", "kvh_wy",  "kvh_wz",  "kvh_ax",  "kvh_ay",  "kvh_az",  "kvh_status",  'kvh_seq_num',  'kvh_Temperature']
        self.__integration[DataNameList[0]] = imudata["TIME"]
        self.__integration[DataNameList[1]] = imudata["WX"]
        self.__integration[DataNameList[2]] = imudata["WY"]
        self.__integration[DataNameList[3]] = imudata["WZ"]
        self.__integration[DataNameList[4]] = imudata["AX"]
        self.__integration[DataNameList[5]] = imudata["AY"]
        self.__integration[DataNameList[6]] = imudata["AZ"]
        self.__integration[DataNameList[7]] = imudata["PD_TEMP_X"]
        self.__integration[DataNameList[8]] = imudata["PD_TEMP_Y"]
        self.__integration[DataNameList[9]] = imudata["PD_TEMP_Z"]
        #VBOX
        self.__integration[DataNameList[12]] = VB_data[DataNameList[12]]
        self.__integration[DataNameList[13]] = VB_data[DataNameList[13]]
        self.__integration[DataNameList[14]] = VB_data[DataNameList[14]]
        self.__integration[DataNameList[15]] = VB_data[DataNameList[15]]
        self.__integration[DataNameList[16]] = VB_data[DataNameList[16]]
        self.__integration[DataNameList[17]] = VB_data[DataNameList[17]]
        self.__integration[DataNameList[18]] = VB_data[DataNameList[18]]
        self.__integration[DataNameList[19]] = VB_data[DataNameList[19]]
        self.__integration[DataNameList[20]] = VB_data[DataNameList[20]]
        self.__integration[DataNameList[21]] = VB_data[DataNameList[21]]
        self.__integration[DataNameList[22]] = VB_data[DataNameList[22]]
        self.__integration[DataNameList[23]] = VB_data[DataNameList[23]]
        self.__integration[DataNameList[24]] = VB_data[DataNameList[24]]
        self.__integration[DataNameList[25]] = VB_data[DataNameList[25]]
        self.__integration[DataNameList[26]] = VB_data[DataNameList[26]]
        self.__integration[DataNameList[27]] = VB_data[DataNameList[27]]
        self.__integration[DataNameList[28]] = VB_data[DataNameList[28]]
        self.__integration[DataNameList[29]] = VB_data[DataNameList[29]]
        self.__integration[DataNameList[30]] = VB_data[DataNameList[30]]
        self.__integration[DataNameList[31]] = VB_data[DataNameList[31]]
        self.__integration[DataNameList[32]] = VB_data[DataNameList[32]]
        self.__integration[DataNameList[33]] = VB_data[DataNameList[33]]
        self.__integration[DataNameList[34]] = VB_data[DataNameList[34]]
        self.__integration[DataNameList[35]] = VB_data[DataNameList[35]]
        # KVH
        self.__integration[DataNameList[36]] = KVHRowData[DataNameList[36]]
        self.__integration[DataNameList[37]] = KVHRowData[DataNameList[37]]
        self.__integration[DataNameList[38]] = KVHRowData[DataNameList[38]]
        self.__integration[DataNameList[39]] = KVHRowData[DataNameList[39]]
        self.__integration[DataNameList[40]] = KVHRowData[DataNameList[40]]
        self.__integration[DataNameList[41]] = KVHRowData[DataNameList[41]]
        self.__integration[DataNameList[42]] = KVHRowData[DataNameList[42]]
        self.__integration[DataNameList[43]] = KVHRowData[DataNameList[43]]
        self.__integration[DataNameList[44]] = KVHRowData[DataNameList[44]]
        # print(KVHRowData)
        # VBrange = 10-len(VB_data["GPS"])
        # for i in range(VBrange):
        #     self.__integration["GPS"] = np.append(self.__integration["GPS"], VB_data["GPS"])
        #     self.__integration["GLONASS"] = np.append(self.__integration["GLONASS"], VB_data["GLONASS"])
        #     self.__integration["BeiDou"] = np.append(self.__integration["BeiDou"], VB_data["BeiDou"])
        #     self.__integration["Time"] = np.append(self.__integration["Time"], VB_data["Time"])
        #     self.__integration["Latitude"] = np.append(self.__integration["Latitude"],VB_data["Latitude"])
        #     self.__integration["Latitude"] = np.append(self.__integration["Latitude"] ,VB_data["Latitude"])
        #     self.__integration["Velocity"] = np.append(self.__integration["Velocity"] ,VB_data["Velocity"])
        #     self.__integration["Heading"] = np.append(self.__integration["Heading"], VB_data["Heading"])
        #     self.__integration["Altitude"] = np.append(self.__integration["Altitude"], VB_data["Altitude"])
        #     self.__integration["Vertical_Vel"] = np.append(self.__integration["Vertical_Vel"], VB_data["Vertical_Vel"])
        #     self.__integration["Pitch_KF"] = np.append(self.__integration["Pitch_KF"], VB_data["Pitch_KF"])
        #     self.__integration["Roll_KF"] = np.append(self.__integration["Roll_KF"], VB_data["Roll_KF"])
        #     self.__integration["Heading_KF"] = np.append(self.__integration["Heading_KF"], VB_data["Heading_KF"])
        #     self.__integration["Pitch_rate"] = np.append(self.__integration["Pitch_rate"], VB_data["Pitch_rate"])
        #     self.__integration["Roll_rate"] = np.append(self.__integration["Roll_rate"], VB_data["Roll_rate"])
        #     self.__integration["Yaw_rate"] = np.append(self.__integration["Yaw_rate"], VB_data["Yaw_rate"])
        #     self.__integration["Acc_X"] = np.append(self.__integration["Acc_X"], VB_data["Acc_X"])
        #     self.__integration["Acc_Y"] = np.append(self.__integration["Acc_Y"], VB_data["Acc_Y"])
        #     self.__integration["Acc_Z"] = np.append(self.__integration["Acc_Z"], VB_data["Acc_Z"])
        #     self.__integration["Date"] = np.append(self.__integration["Date"], VB_data["Date"])
        #     self.__integration["KF_Status"] = np.append(self.__integration["KF_Status"], VB_data["KF_Status"])
        #     self.__integration["Pos_Quality"] = np.append(self.__integration["Pos_Quality"], VB_data["Pos_Quality"])
        #     self.__integration["Vel_Quality"] = np.append(self.__integration["Vel_Quality"], VB_data["Vel_Quality"])
        #     self.__integration["Heading2_KF"] = np.append(self.__integration["Heading2_KF"], VB_data["Heading2_KF"])
        #
        if not __name__ == "__main__":
            self.timePointData_signal.emit(self.__integration)


    def cleanStruck(self):
        self.__integration = {k: np.empty(0) for k in set(Integration_DATA_STRUCTURE)}

    def ConvertToMapValue(self, valArray, VB):
        #self.cleanStruck()
        #print(valArray["TIME"][0])
        getMapValArr = np.array([])
        turnAngArr = np.array([])
        if len(self.__realTM) == 0:
            for i in range(10):
                self.initKM.SetPosLatLong(VB["Latitude"][i], VB["Longitude"][i])
                turnAng = -self.initKM.getAngle()

                if len(getMapValArr) == 0:
                    getMapValArr = np.array([[VB["Latitude"][i], VB["Longitude"][i]]])
                else:
                    latlngNp = np.array([VB["Latitude"][i], VB["Longitude"][i]])

                    getMapValArr = np.vstack([getMapValArr, latlngNp])
                turnAngArr = np.append(turnAngArr, turnAng)
                self.__integration["One_latitude(deg)"] = np.append(self.__integration["One_latitude(deg)"], VB["Latitude"][i])
                self.__integration["One_longitude(deg)"] = np.append(self.__integration["One_longitude(deg)"], VB["Longitude"][i])

        if len(self.__realTM) > 0:
            for i in range(10):
                angularVelocity = np.array([valArray["WX"][i], valArray["WY"][i], valArray["WZ"][i]])
                acceleration = np.array([valArray["AX"][i], valArray["AY"][i], valArray["AZ"][i]])
                self.initKM.run(valArray["TIME"][i], angularVelocity, acceleration)
                getMapVal = self.initKM.getPosition()
                turnAng = -self.initKM.getAngle()

                if len(getMapValArr) == 0:
                    getMapValArr = np.array([[getMapVal[0], getMapVal[1]]])
                else:
                    latlngNp = np.array([getMapVal[0], getMapVal[1]])

                    getMapValArr = np.vstack([getMapValArr, latlngNp])
                turnAngArr = np.append(turnAngArr, turnAng)
                self.__integration["One_latitude(deg)"] = np.append(self.__integration["One_latitude(deg)"], getMapVal[0])
                self.__integration["One_longitude(deg)"] = np.append(self.__integration["One_longitude(deg)"], getMapVal[1])

        return getMapValArr, turnAngArr

    def cleanArray(self):
        self.initKM = Driving()
        self.realTMArr = []
        self.realTM = []