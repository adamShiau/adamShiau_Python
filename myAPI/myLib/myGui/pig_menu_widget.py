from PyQt5.QtWidgets import *


class pig_menu_widget:
    def __init__(self, menu, obj):
        self.pig_para_action = None
        self.myMenu = menu.addMenu("Setting")
        self.action_list(obj)

    def action_list(self, obj):
        self.pig_para_action = QAction("pig parameters", obj)
        self.pig_para_action.setShortcut("Ctrl+P")
        self.pig_para_action.setEnabled(False)
        self.myMenu.addAction(self.pig_para_action)

    def action_trigger_connect(self, fn):
        self.pig_para_action.triggered.connect(fn)

    def setEnable(self, open):
        self.pig_para_action.setEnabled(open)