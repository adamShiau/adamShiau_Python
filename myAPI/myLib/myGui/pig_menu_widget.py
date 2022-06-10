from PyQt5.QtWidgets import *


class pig_menu_widget:
    def __init__(self, menuBar, obj):
        self.pig_cali_action = None
        self.pig_para_action = None
        self.myMenu = menuBar.addMenu("Setting")
        self.action_list(obj)

    def action_list(self, obj):
        self.pig_para_action = QAction("pig parameters", obj)
        self.pig_para_action.setShortcut("Ctrl+P")
        self.pig_para_action.setEnabled(False)
        self.pig_cali_action = QAction("pig calibration", obj)
        self.pig_cali_action.setShortcut("Ctrl+k")
        self.pig_cali_action.setEnabled(True)
        self.myMenu.addAction(self.pig_para_action)
        self.myMenu.addAction(self.pig_cali_action)

    def action_trigger_connect(self, fn):
        self.pig_para_action.triggered.connect(fn[0])
        self.pig_cali_action.triggered.connect(fn[1])

    def setEnable(self, open):
        self.pig_para_action.setEnabled(open)
        self.pig_cali_action.setEnabled(not open)