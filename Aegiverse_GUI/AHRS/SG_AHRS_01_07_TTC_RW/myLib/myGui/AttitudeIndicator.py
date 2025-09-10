""" ####### log stuff creation, always on the top ########  """
import builtins
import os
from myLib.logProcess import logProcess

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "AIndicator_logger"

logProcess.fileStartedInfo(logger_name, ExternalName_log)
""" ####### end of log stuff creation ########  """

import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QTransform, QPixmap, QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsItem, QLabel, \
    QGraphicsProxyWidget, QGraphicsRectItem, QGraphicsTextItem
import myLib.myGui.AttitudeIndicatorImg_rc


class AttitudeIndicator_view_processing(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setFixedSize(470, 580) #20250205 height -> 630
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setInteractive(False)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        # 場景大小
        self.setSceneRect(115, 968, 500, 578)

        self.__moveDistanceX_old = 0
        self.__moveDistanceY_old = 0
        self.__moveDistanceX_new = 0
        self.__moveDistanceY_new = 0
        self.__rotate_angle = 0
        self.__pitch_angle = 0


        self.flightUI()


    def flightUI(self):
        # 當pitch超過180度，會接到另一圖層
        background_pixmap = QPixmap(":/images/background.tiff")
        self.background_height = 350

        self.background_img = QPixmap(background_pixmap)
        self.background_Item1 = QGraphicsPixmapItem(self.background_img)
        self.background_Item1.setTransformationMode(Qt.SmoothTransformation)
        self.background_Item1.setPos(-758, 200)
        self.background_Item1.setZValue(0)
        # 設定底圖旋轉的中心點位置
        self.background_Item1.setTransformOriginPoint(self.background_img.width()/2 +2, self.background_img.height()/2)
        self.scene.addItem(self.background_Item1)


        self.planeAxis_img = QPixmap(":/images/airplaneAxis_6_1.png")  # 先將原圖百分比縮50%，再將縮的圖再縮至80%
        self.planeAxis_Item = QGraphicsPixmapItem(self.planeAxis_img)
        self.planeAxis_Item.setPos(167, 1010)
        self.planeAxis_Item.setZValue(6)
        self.scene.addItem(self.planeAxis_Item)
        self.planeAxis_Item.setTransformOriginPoint(self.planeAxis_img.width()/2, self.planeAxis_img.height()/2)

        self.outFrame_img = QPixmap(":/images/roll_outerFrame_yawTwo_8_1.tiff")
        self.outFrame_Item = QGraphicsPixmapItem(self.outFrame_img)
        self.outFrame_Item.setPos(66.5, 942) # 64, 874
        self.outFrame_Item.setZValue(5)
        self.scene.addItem(self.outFrame_Item)

        self.yaw_img = QPixmap(":/images/yaw_rule5_2.tiff")
        self.yaw_Item3 = QGraphicsPixmapItem(self.yaw_img)
        self.yaw_Item3.setTransformationMode(Qt.SmoothTransformation)
        self.yaw_Item3.setPos(101, 1459)
        self.yaw_Item3.setZValue(5)
        self.yaw_Item3.setTransformOriginPoint(self.yaw_img.width() / 2, self.yaw_img.height() / 2)
        self.scene.addItem(self.yaw_Item3)

        # 顯示皮尺的數值(圖示部分)
        self.yaw_text_img = QPixmap(":/images/show_yaw_data_img2.png")
        self.yaw_text_Item = QGraphicsPixmapItem(self.yaw_text_img)
        self.yaw_text_Item.setPos(309, 1415)  # 1420
        self.yaw_text_Item.setZValue(5)
        self.scene.addItem(self.yaw_text_Item)

        self.yaw_text = QLabel()
        self.yaw_text.setFixedSize(42, 22)
        # background - image: url('show_yaw_data_img1_2.png');
        self.yaw_text.setStyleSheet("""
                                    QLabel{
                                        background-repeat: no-repeat;
                                        background-position: center;
                                        color: black;
                                        font-size: 18px;
                                    }
                                """)
        self.yaw_text.setText("0")
        self.yaw_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        SceneWidget = QGraphicsProxyWidget()
        SceneWidget.setWidget(self.yaw_text)
        SceneWidget.setPos(332, 1430)
        SceneWidget.setZValue(6)
        self.scene.addItem(SceneWidget)

        # 提示出現錯誤
        self.__err_rect = QGraphicsRectItem(QRectF(110.5, 958, 500, 450))
        self.__err_rect.setBrush(QBrush(QColor(10, 10, 10, 90)))
        self.__err_rect.setPen(QPen(Qt.NoPen))
        self.__err_rect.setZValue(7)
        self.__err_text = QGraphicsTextItem("Invalid data here")
        self.__err_text.setDefaultTextColor(QColor("red"))
        self.__err_text.setPos(270.5, 1152)
        self.__err_text.setFont(QFont("Arial", 16))
        self.__err_text.setZValue(8)


    def roll_flight_axis_update_rotation(self, roll_val):
        self.__rotate_angle = roll_val
        if self.__rotate_angle < -180:
            self.__rotate_angle = -180
        if self.__rotate_angle > 180:
            self.__rotate_angle = 180


    def pitch_flight_update_translate(self, pitch_val):
        self.__pitch_angle = pitch_val
        if self.__pitch_angle < -90:
            self.__pitch_angle = -90
        if self.__pitch_angle > 90:
            self.__pitch_angle = 90


    def updateView(self):
        self.updateRollPitch()
        self.__moveDistanceX_old  = self.__moveDistanceX_new
        self.__moveDistanceY_old  = self.__moveDistanceY_new


    def updateRollPitch(self):
        self.background_Item1.setRotation(self.__rotate_angle)
        self.planeAxis_Item.setRotation(self.__rotate_angle)

        Itemradians = math.radians(-self.__rotate_angle)  # 計算旋轉的弧度
        movementVal = 8.23 * (-self.__pitch_angle)  # 計算pitch從原點0，移動到該刻度的數值

        self.__moveDistanceX_new = movementVal * math.sin(Itemradians) # 新的平移量
        self.__moveDistanceY_new = movementVal * math.cos(Itemradians) # 新的平移量

        # 計算相對位置(新的移動值減舊的移動值)
        self.background_Item1.moveBy(self.__moveDistanceX_new - self.__moveDistanceX_old, self.__moveDistanceY_new - self.__moveDistanceY_old)
        # except TypeError:
        #     # 因為此結果是為了顯示UI，但UI並沒有地方可以直接顯示文字，所以只寫log通知使用者，然後
        #     # 請確認計算pitche與roll的資料，是否有使用到不同型態(字串、布林值...)的資料，若有使用到不同型態的資料，請檢查並修正，謝謝。
        #     logProcess.centrailzedError(num="", content="Please verify whether the data used to calculate pitch and roll contains mixed data types (e.g., strings, booleans)."
        #                                                 " If it does, kindly review and correct them. Thank you.", fileName=ExternalName_log)
        #     self.scene.addItem(self.__err_rect)
        #     self.scene.addItem(self.__err_text)

        # 更新畫面
        self.scene.update()


    def yaw_flight_update_move(self, yaw_val):
        self.yaw_Item3.setRotation(yaw_val)
        self.__yawval = "0"
        if yaw_val > 0:
            yawVal = 360 - yaw_val
            self.__yawval = f'{yawVal:.0f}'
        if yaw_val < 0:
            self.__yawval = f'{(-yaw_val):.0f}'
        self.yaw_text.setText(str(self.__yawval))
        self.scene.update()

