import sys

from PySide6.QtWidgets import QGridLayout, QApplication, QWidget
from myLib.myGui.mygui_serial import spinBlock



class pigKalParaWidget(QWidget):
    def __init__(self, act):
        super(pigKalParaWidget, self).__init__()
        self.__act = act
        self.setWindowTitle("Setting Kalman")
        self.resize(250, 100)
        #self.KF_Q = spinBlock(title='Process Noise Variance(Q/R)', minValue=1, maxValue=1e9, double=False, step=1)
        self.KF_R = spinBlock(title='Ratio Parameter(R/Q)', minValue=1, maxValue=1e9, double=False, step=1)
        self.initUI()
        self.linkfunction()


    def initUI(self):
        layout = QGridLayout()
        #layout.addWidget(self.KF_Q, 0, 0, 1, 2)
        layout.addWidget(self.KF_R, 0, 2, 1, 2)
        self.setLayout(layout)


    def linkfunction(self):
        #self.KF_Q.spin.valueChanged.connect(self.update_KF_Q)
        self.KF_R.spin.valueChanged.connect(self.update_KF_R)


    # def init_write_para(self, initPara):
    #     #self.KF_Q.spin.setValue(initPara["Process_Noise"])
    #     self.KF_R.spin.setValue()
    #     self.update_KF_Q()


    # def update_KF_Q(self):
    #     value = self.KF_Q.spin.value()
    #     self.__act.kal_Q = value


    def update_KF_R(self):
        value = self.KF_R.spin.value()
        self.__act.kal_R = value




if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigKalParaWidget("act")
    w.show()
    app.exec_()