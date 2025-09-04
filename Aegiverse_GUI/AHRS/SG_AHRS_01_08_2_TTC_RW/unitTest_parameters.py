import unittest
from unittest.mock import patch, MagicMock


from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMessageBox

from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from pigImuReader import pigImuReader
from myLib.mySerial.Connector import Connector

class unitTestParameter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication.instance() is None:
            cls.test_app = QApplication([])
        else:
            cls.test_app = QApplication.instance()

    @classmethod
    def tearDownClass(cls):
        QApplication.instance().quit()
        cls.test_app = None
        QTest.qWait(100)
        cls.test_app = None


    def setUp(self):
        self.act = pigImuReader()
        self.paraWid = pig_parameters_widget(self.act)

    #
    def test_para_changeValue_Controller_backgroundColor_turnTo_yellow(self):
        self.paraWid.wait_cnt.spin.setValue(10)
        self.paraWid.avg.spin.setValue(5)
        self.paraWid.mod_H.spin.setValue(522)
        self.paraWid.mod_L.spin.setValue(352)
        self.paraWid.freq.spin.setValue(120)
        self.paraWid.err_th.spin.setValue(78)
        self.paraWid.err_offset.spin.setValue(105)
        self.paraWid.polarity.spin.setValue(0)
        self.paraWid.const_step.spin.setValue(3120)
        self.paraWid.KF_Q.spin.setValue(5)
        self.paraWid.KF_R.spin.setValue(2)
        self.paraWid.HD_Q.spin.setValue(42)
        self.paraWid.HD_R.spin.setValue(31)
        self.paraWid.gain1.spin.setValue(7)
        self.paraWid.gain2.spin.setValue(6)
        self.paraWid.fb_on.spin.setValue(0)
        self.paraWid.dac_gain.spin.setValue(51)
        self.paraWid.cutoff.spin.setValue(550)
        self.paraWid.sf0.le.setText("0.021")
        self.paraWid.sf1.le.setText("0.254")
        self.paraWid.T1.le.setText("20.5")
        self.paraWid.T2.le.setText("55.0")
        self.paraWid.slope1.le.setText("0.0002155")
        self.paraWid.slope2.le.setText("0.00525")
        self.paraWid.slope3.le.setText("0.0000445")
        self.paraWid.offset1.le.setText("0.000000453")
        self.paraWid.offset2.le.setText("0.00000528")
        self.paraWid.offset3.le.setText("0.00042527")
        self.paraWid.dac_Vpi.le.setText("1.057")
        self.paraWid.rst_voltage.le.setText("12")
        # 判斷是否有改變背景
        controller_arr = [self.paraWid.wait_cnt.spin, self.paraWid.avg.spin, self.paraWid.mod_H.spin, self.paraWid.mod_L.spin, self.paraWid.freq.spin,
                          self.paraWid.err_th.spin, self.paraWid.err_offset.spin, self.paraWid.polarity.spin, self.paraWid.const_step.spin, self.paraWid.KF_Q.spin,
                          self.paraWid.KF_R.spin, self.paraWid.HD_Q.spin, self.paraWid.HD_R.spin, self.paraWid.gain1.spin, self.paraWid.gain2.spin, self.paraWid.fb_on.spin, self.paraWid.dac_gain.spin,
                          self.paraWid.cutoff.spin, self.paraWid.sf0.le, self.paraWid.sf1.le, self.paraWid.T1.le, self.paraWid.T2.le, self.paraWid.slope1.le, self.paraWid.slope2.le,
                          self.paraWid.slope3.le, self.paraWid.offset1.le, self.paraWid.offset2.le, self.paraWid.offset3.le, self.paraWid.dac_Vpi.le, self.paraWid.rst_voltage.le]
        stylesheet_color = "background-color:yellow"

        for Item in controller_arr:
            self.assertTrue(stylesheet_color, Item.styleSheet())

    # 測試button功能，觸發會跳出視窗，確認是否更新
    @patch('myLib.myGui.pig_parameters_widget.pig_parameters_widget.updatelink')
    def test_changeValue_and_trigger_updateBtn(self, mock_func):
        # 輸入的值
        self.paraWid.wait_cnt.spin.setValue(10)
        self.paraWid.avg.spin.setValue(5)
        self.paraWid.mod_H.spin.setValue(522)
        self.paraWid.mod_L.spin.setValue(352)
        self.paraWid.freq.spin.setValue(120)
        self.paraWid.err_th.spin.setValue(78)
        self.paraWid.err_offset.spin.setValue(105)
        self.paraWid.polarity.spin.setValue(0)
        self.paraWid.const_step.spin.setValue(3120)
        self.paraWid.KF_Q.spin.setValue(5)
        self.paraWid.KF_R.spin.setValue(2)
        self.paraWid.HD_Q.spin.setValue(42)
        self.paraWid.HD_R.spin.setValue(31)
        self.paraWid.gain1.spin.setValue(7)
        self.paraWid.gain2.spin.setValue(6)
        self.paraWid.fb_on.spin.setValue(0)
        self.paraWid.dac_gain.spin.setValue(51)
        self.paraWid.cutoff.spin.setValue(550)
        self.paraWid.sf0.le.setText("0.021")
        self.paraWid.sf1.le.setText("0.254")
        self.paraWid.T1.le.setText("20.5")
        self.paraWid.T2.le.setText("55.0")
        self.paraWid.slope1.le.setText("0.0002155")
        self.paraWid.slope2.le.setText("0.00525")
        self.paraWid.slope3.le.setText("0.0000445")
        self.paraWid.offset1.le.setText("0.000000453")
        self.paraWid.offset2.le.setText("0.00000528")
        self.paraWid.offset3.le.setText("0.00042527")
        self.paraWid.dac_Vpi.le.setText("1.057")
        self.paraWid.rst_voltage.le.setText("12")

        QTimer.singleShot(3000, self.get_window_choose_update_yesOrNo)
        updateBtn = self.paraWid.updateBtn
        QTest.mouseClick(updateBtn, Qt.LeftButton)
        QTest.qWait(5000)

        # 確認有被呼叫執行
        mock_func.assert_called()

    def get_window_choose_update_yesOrNo(self):
        getWidgets = QApplication.topLevelWidgets()
        update_mes_box = None
        for mesWidget in getWidgets:
            if isinstance(mesWidget, QMessageBox):
                update_mes_box = mesWidget
                break

        self.assertIsNotNone(update_mes_box)
        self.assertEqual(update_mes_box.text(), "請確認被選中的控制項都是要修改數值嗎?")

        YesBtn = update_mes_box.button(QMessageBox.Yes)
        YesBtn.click()


    # 測試需要更新的參數是否被執行(取得被執行的多個function log)
    @patch('myLib.myGui.pig_parameters_widget.logger.info')
    @patch('serial.Serial')
    def test_update_input_para_to_device(self, mock_serial, mock_get_info_log):
        conn = Connector()
        setattr(conn, "_Connector__ser", MagicMock())
        setattr(conn, "_Connector__baudRate", 230400)
        setattr(conn, "_Connector__portName", "COM2")

        mock_serial.return_value = getattr(conn, "_Connector__ser")
        mock_serial.return_value.is_open = True

        self.act.connect(conn, "COM2", 230400)

        self.paraWid.sf0.le.setText("0.021")
        self.paraWid.sf1.le.setText("0.254")
        self.paraWid.T1.le.setText("10.0")
        self.paraWid.T2.le.setText("45.5")
        self.paraWid.slope1.le.setText("0.0000454885")
        self.paraWid.slope2.le.setText("0.2445487422")
        self.paraWid.slope3.le.setText("0.0021484884")
        self.paraWid.offset1.le.setText("0.0187420544")
        self.paraWid.offset2.le.setText("0.055848747")
        self.paraWid.offset3.le.setText("0.0649420535")
        self.paraWid.dac_Vpi.le.setText("1.584")
        self.paraWid.rst_voltage.le.setText("12")

        QTimer.singleShot(3000, self.get_window_choose_update_yesOrNo)

        updateBtn_trigger = self.paraWid.updateBtn
        QTest.mouseClick(updateBtn_trigger, Qt.LeftButton)

        log_contents = [log[0] for log, _ in mock_get_info_log.call_args_list]
        info_conetent_arr = ["set wait cnt","set err_avg","set mod_H","set mod_L","set freq","set err_th","set err offset","set polarity","set constant step",
                             "set KF_Q","set KF_R","set HD_Q","set HD_R","set gain1","set gain2","set FB on","set DAC gain","set CUTOFF","set dataRate","set offset3",]

        i = 0
        while i < len(info_conetent_arr):
            self.assertIn(info_conetent_arr[i], log_contents[i])
            i += 1
            continue

        QTest.qWait(5000)



    def test_init_value_controller_TCycling(self):
        para_arr = {'FREQ': 205, 'MOD_H': 8550, 'MOD_L': -8550, 'ERR_OFFSET': 0, 'POLARITY': 1, 'WAIT_CNT': 12, 'ERR_TH': 0, 'ERR_AVG': 8, 'GAIN1': 3, 'GAIN2': 5, 'FB_ON': 1,
                    'CONST_STEP': 13254, 'HD_Q': 1, 'HD_R': 6, 'SF0': 0.000165805366, 'SF1': 0.00018698, 'SF2': 0.0001, 'SF3': 0.0001, 'SF4': 0.0001, 'SF5': 0.0001, 'SF6': 0.0001,
                    'SF7': 0.0001, 'SF8': 0.0001, 'SF9': 0.0001, 'TMIN': -20, 'T1': -10, 'T2': 0, 'T3': 10, 'T4': 20, 'T5': 30, 'T6': 40, 'T7': 50, 'TMAX': 80,
                    'DAC_GAIN': 103, 'DATA_RATE': 2000, 'SFB': 0.0, 'CUTOFF': 1143111680, 'BIAS_COMP_T1': -10.0, 'BIAS_COMP_T2': 40.0, 'SFB_1_SLOPE': 0.00426748475,
                    'SFB_1_OFFSET': 1.000000000045, 'SFB_2_SLOPE': 0.05274532635, 'SFB_2_OFFSET': 0.2548844610, 'SFB_3_SLOPE': 0.0021548798, 'SFB_3_OFFSET': 0.02416595133}

        
        self.paraWid.set_init_value(para_arr)

        self.assertEqual(1.658054 , float(self.paraWid.sf0.le.text()))
        self.assertEqual(1.8698, float(self.paraWid.sf1.le.text()))
        self.assertEqual(-10.0, float(self.paraWid.T1.le.text()))
        self.assertEqual(40.0, float(self.paraWid.T2.le.text()))
        self.assertEqual(0.0042674847, float(self.paraWid.slope1.le.text()))
        self.assertEqual(0.0527453264, float(self.paraWid.slope2.le.text()))
        self.assertEqual(0.0021548798, float(self.paraWid.slope3.le.text()))
        self.assertEqual(1.0 , float(self.paraWid.offset1.le.text()))
        self.assertEqual(0.254884461 , float(self.paraWid.offset2.le.text()))
        self.assertEqual(0.0241659513, float(self.paraWid.offset3.le.text()))

        # 判斷是否有將背景變回白色
        controller_arr = [self.paraWid.wait_cnt.spin, self.paraWid.avg.spin, self.paraWid.mod_H.spin,
                          self.paraWid.mod_L.spin, self.paraWid.freq.spin,
                          self.paraWid.err_th.spin, self.paraWid.err_offset.spin, self.paraWid.polarity.spin,
                          self.paraWid.const_step.spin, self.paraWid.KF_Q.spin,
                          self.paraWid.KF_R.spin, self.paraWid.HD_Q.spin, self.paraWid.HD_R.spin,
                          self.paraWid.gain1.spin, self.paraWid.gain2.spin, self.paraWid.fb_on.spin,
                          self.paraWid.dac_gain.spin,
                          self.paraWid.cutoff.spin, self.paraWid.sf0.le, self.paraWid.sf1.le, self.paraWid.T1.le,
                          self.paraWid.T2.le, self.paraWid.slope1.le, self.paraWid.slope2.le,
                          self.paraWid.slope3.le, self.paraWid.offset1.le, self.paraWid.offset2.le,
                          self.paraWid.offset3.le, self.paraWid.dac_Vpi.le, self.paraWid.rst_voltage.le]
        stylesheet_color = "background-color:white"

        for Item in controller_arr:
            self.assertTrue(stylesheet_color, Item.styleSheet())


    def tearDown(self):
        patch.stopall()
        self.paraWid = None

if __name__=="__main__":
    unittest.main()