# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging



if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PySide6.QtWidgets import *
from PySide6.QtGui import QAction

class pig_menu_manager:
    def __init__(self, menuBar, obj):
        self.hins_cmd_action = None
        self.pig_version_action = None
        self.pig_initial_setting_action = None
        self.pig_plot_action = None
        self.pig_allan_action = None
        self.pig_cali_action = None
        self.pig_para_action = None
        self.pig_config_action = None

        self.file_menu = menuBar.addMenu("File")
        self.setting_menu = menuBar.addMenu("Setting")
        # self.analysis_menu = menuBar.addMenu("Analysis")
        self.action_list(obj)

    def action_list(self, obj):
        
        """version menu"""
        self.pig_version_action = QAction("version")
        self.pig_version_action.setEnabled(False)
        self.file_menu.addAction(self.pig_version_action)
        '''fog parameter setting'''
        self.pig_para_action = QAction("Parameters", obj)
        self.pig_para_action.setShortcut("Ctrl+P")
        self.pig_para_action.setEnabled(False)
        self.setting_menu.addAction(self.pig_para_action)

        '''fog and accl misalignment setting'''
        self.pig_W_A_cali_action = QAction("Calibration parameters", obj)
        self.pig_W_A_cali_action.setShortcut("Ctrl+m")
        self.pig_W_A_cali_action.setEnabled(False)
        self.setting_menu.addAction(self.pig_W_A_cali_action)

        '''fog configuration setting'''
        self.pig_config_action = QAction("Configuration", obj)
        self.pig_config_action.setShortcut("Ctrl+C")
        self.pig_config_action.setEnabled(False)
        self.setting_menu.addAction(self.pig_config_action)

        '''HINS CMD setting'''
        self.hins_cmd_action = QAction("HINS_Config", obj)
        self.hins_cmd_action.setShortcut("Ctrl+h")
        self.hins_cmd_action.setEnabled(False)
        self.setting_menu.addAction(self.hins_cmd_action)

        '''
        self.pig_cali_action = QAction("pig calibration", obj)
        self.pig_cali_action.setShortcut("Ctrl+k")
        self.pig_cali_action.setEnabled(True)
        self.setting_menu.addAction(self.pig_cali_action)
        
        self.pig_initial_setting_action = QAction("pig initial setting", obj)
        self.pig_initial_setting_action.setShortcut("Ctrl+i")
        self.pig_initial_setting_action.setEnabled(True)
        self.setting_menu.addAction(self.pig_initial_setting_action)
        '''
        '''
        self.pig_allan_action = QAction("Allan Deviation", obj)
        self.pig_allan_action.setShortcut("Ctrl+A")
        self.pig_plot_action = QAction("Plot Timing Data", obj)
        self.pig_plot_action.setShortcut("Ctrl+T")
        self.analysis_menu.addAction(self.pig_plot_action)
        self.analysis_menu.addAction(self.pig_allan_action)
        '''

    def action_trigger_connect(self, fn):
        self.pig_para_action.triggered.connect(fn[0])
        self.pig_W_A_cali_action.triggered.connect(fn[1])
        self.pig_version_action.triggered.connect(fn[2])
        self.pig_config_action.triggered.connect(fn[3])
        self.hins_cmd_action.triggered.connect(fn[4])
        # self.pig_cali_action.triggered.connect(fn[1])
        # self.pig_plot_action.triggered.connect(fn[2])
        # self.pig_allan_action.triggered.connect(fn[3])
        # self.pig_initial_setting_action.triggered.connect(fn[4])


    def setEnable(self, open):
        self.pig_para_action.setEnabled(open)
        self.pig_W_A_cali_action.setEnabled(open)
        self.pig_version_action.setEnabled(open)
        self.pig_config_action.setEnabled(open)
        self.hins_cmd_action.setEnabled(open)
        # self.pig_cali_action.setEnabled(not open)
        # self.pig_initial_setting_action.setEnabled(not open)