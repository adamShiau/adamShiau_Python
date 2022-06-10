import common as cmn

'''-------define CMD address map-------'''
'''0~7 for output mode setting'''
'''8~255 for parameter setting'''
MODE_STOP = 0
MODE_FOG = 1
MODE_IMU = 2
MODE_EQ = 3
MODE_IMU_FAKE = 4
CMD_FOG_MOD_FREQ = 8
CMD_FOG_MOD_AMP_H = 9
CMD_FOG_MOD_AMP_L = 10
CMD_FOG_ERR_OFFSET = 11
CMD_FOG_POLARITY = 12
CMD_FOG_WAIT_CNT = 13
CMD_FOG_ERR_TH = 14
CMD_FOG_ERR_AVG = 15
CMD_FOG_TIMER_RST = 16
CMD_FOG_GAIN1 = 17
CMD_FOG_GAIN2 = 18
CMD_FOG_FB_ON = 19
CMD_FOG_CONST_STEP = 20
CMD_FOG_FPGA_Q = 21
CMD_FOG_FPGA_R = 22
CMD_FOG_DAC_GAIN = 23
CMD_FOG_INT_DELAY = 24
CMD_FOG_OUT_START = 25

'''FOG OUTPUT MODE'''
INT_SYNC = 1
EXT_SYNC = 2
STOP_SYNC = 4

''' FOG PARAMETERS'''
INIT_PARAMETERS = {"MOD_H": 6850,
                   "MOD_L": -6850,
                   "FREQ": 135,
                   "DAC_GAIN": 20,
                   "ERR_OFFSET": 0,
                   "POLARITY": 1,
                   "WAIT_CNT": 65,
                   "ERR_TH": 0,
                   "ERR_AVG": 6,
                   "GAIN1": 6,
                   "GAIN2": 5,
                   "FB_ON": 1,
                   "CONST_STEP": 0,
                   "KF_Q": 1,
                   "KF_R": 6,
                   "SF_A": 0.00075,
                   "SF_B": -0.00137052112589694,
                   "DATA_RATE": 2296
                   }


'''FPGA OUTPUT COEFFICIENT'''
ADC_COEFFI = 4000 / 8192
TIME_COEFFI = 1e-4

"""FOG HEADER"""
HEADER_PIG = [0xFE, 0x81, 0xFF, 0x55]  # 254, 129, 255, 85

"""MEMS GYRO & XLM SCALE FACTOR"""
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
SENS_ADXL355_8G = 0.0000156

class pig_parameters_ros:
    def __init__(self, act):
        self.__act = act
        self.__par_manager = cmn.parameters_manager("parameters_SP9.json", INIT_PARAMETERS, 1)
        initPara = self.__par_manager.check_file_exist()
        self.set_init_value(initPara)

    def set_init_value(self, para):
        self.send_FREQ_CMD(para["FREQ"])
        self.send_WAIT_CNT_CMD(para["WAIT_CNT"])
        self.send_AVG_CMD(para["ERR_AVG"])
        self.send_MOD_H_CMD(para["MOD_H"])
        self.send_MOD_L_CMD(para["MOD_L"])
        self.send_ERR_TH_CMD(para["ERR_TH"])
        self.send_ERR_OFFSET_CMD(para["ERR_OFFSET"])
        self.send_POLARITY_CMD(para["POLARITY"])
        self.send_CONST_STEP_CMD(para["CONST_STEP"])
        # self.update_KF_Q()
        # self.update_KF_R()
        self.send_GAIN1_CMD(para["GAIN1"])
        self.send_GAIN2_CMD(para["GAIN2"])
        self.send_FB_ON_CMD(para["FB_ON"])
        self.send_DAC_GAIN_CMD(para["DAC_GAIN"])
        self.send_DATA_RATE_CMD(para["DATA_RATE"])
        self.SF_A_EDIT(para["SF_A"])
        self.SF_B_EDIT(para["SF_B"])

    def writeImuCmd(self, cmd, value):
        self.__act.writeImuCmd(cmd, value)

    def send_FREQ_CMD(self, value):
        print('set freq: ', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, value)
        # self.__par_manager.update_parameters("FREQ", value)

    def send_MOD_H_CMD(self, value):
        print('set mod_H: ', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, value)
        # self.__par_manager.update_parameters("MOD_H", value)

    def send_MOD_L_CMD(self, value):
        print('set mod_L: ', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, value)
        # self.__par_manager.update_parameters("MOD_L", value)

    def send_ERR_OFFSET_CMD(self, value):
        print('set err offset: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, value)
        # self.__par_manager.update_parameters("ERR_OFFSET", value)

    def send_POLARITY_CMD(self, value):
        print('set polarity: ', value)
        self.__act.writeImuCmd(CMD_FOG_POLARITY, value)
        # self.__par_manager.update_parameters("POLARITY", value)

    def send_WAIT_CNT_CMD(self, value):
        print('set wait cnt: ', value)
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, value)
        # self.__par_manager.update_parameters("WAIT_CNT", value)

    def send_ERR_TH_CMD(self, value):
        print('set err_th: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_TH, value)
        # self.__par_manager.update_parameters("ERR_TH", value)

    def send_AVG_CMD(self, value):
        print('set err_avg: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, value)
        # self.__par_manager.update_parameters("ERR_AVG", value)

    def send_GAIN1_CMD(self, value):
        print('set gain1: ', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN1, value)
        # self.__par_manager.update_parameters("GAIN1", value)

    def send_GAIN2_CMD(self, value):
        print('set gain2: ', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN2, value)
        # self.__par_manager.update_parameters("GAIN2", value)

    def send_FB_ON_CMD(self, value):
        print('set FB on: ', value)
        self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        # self.__par_manager.update_parameters("FB_ON", value)

    def send_DAC_GAIN_CMD(self, value):
        print('set DAC gain: ', value)
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, value)
        # self.__par_manager.update_parameters("DAC_GAIN", value)

    def send_CONST_STEP_CMD(self, value):
        print('set constant step: ', value)
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, value)
        # self.__par_manager.update_parameters("CONST_STEP", value)

    def send_DATA_RATE_CMD(self, value):
        print('set dataRate: ', value)
        self.__act.writeImuCmd(CMD_FOG_INT_DELAY, value)
        # self.__par_manager.update_parameters("DATA_RATE", value)

    def SF_A_EDIT(self, value):
        print('sf_a: ', value)
        self.__act.sf_a = value
        # self.__par_manager.update_parameters("SF_A", value)

    def SF_B_EDIT(self, value):
        print('sf_b: ', value)
        self.__act.sf_b = value
        # self.__par_manager.update_parameters("SF_B", value)

    # def update_KF_Q(self, value):
    #     value = self.KF_Q.spin.value()
    #     print('KF_Q: ', value)
    #     self.__par_manager.update_parameters("KF_Q", value)

    # def update_KF_R(self, value):
    #     value = self.KF_R.spin.value()
    #     print('KF_R: ', value)
    #     self.__par_manager.update_parameters("KF_R", value)


