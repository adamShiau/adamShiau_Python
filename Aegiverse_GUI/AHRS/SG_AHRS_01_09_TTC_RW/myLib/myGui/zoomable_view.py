# myLib/myGui/zoomable_view.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform, QKeySequence, QShortcut, QPainter  # ← 加上 QPainter
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget
)


class ZoomableView(QGraphicsView):
    """
    用 QGraphicsView 包裝任意 QWidget，支援：
      - Ctrl + 滾輪：縮放
      - 滑鼠中鍵/空白鍵拖曳：平移
      - Ctrl + 0：重置縮放
      - Ctrl + = / Ctrl + +：放大
      - Ctrl + -：縮小
      - 滑鼠雙擊：重置縮放
    """
    def __init__(self, widget: QWidget, parent=None, min_scale=0.6, max_scale=3.0, step=1.12):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self._proxy: QGraphicsProxyWidget = self.scene().addWidget(widget)

        # 這行改用 QPainter.* 常數
        self.setRenderHints(
            self.renderHints()
            | QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)

        # 參數
        self._min_scale = float(min_scale)
        self._max_scale = float(max_scale)
        self._step = float(step)
        self._current_scale = 1.0

        # 快捷鍵
        QShortcut(QKeySequence("Ctrl+="), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.reset_zoom)

        # 初始視角
        self._fit_initial()

    def _fit_initial(self):
        self.fitInView(self._proxy, Qt.KeepAspectRatio)
        # 將當前矩陣歸一化，後續用 _current_scale 管理倍率
        self.setTransform(QTransform())
        self._current_scale = 1.0

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            if angle != 0:
                factor = self._step if angle > 0 else 1.0 / self._step
                self._apply_scale(factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.reset_zoom()
        super().mouseDoubleClickEvent(event)

    def _apply_scale(self, factor: float):
        new_scale = self._current_scale * factor
        new_scale = max(self._min_scale, min(self._max_scale, new_scale))
        if abs(new_scale - self._current_scale) < 1e-6:
            return
        factor_to_apply = new_scale / self._current_scale
        self._current_scale = new_scale
        self.scale(factor_to_apply, factor_to_apply)

    def zoom_in(self):
        self._apply_scale(self._step)

    def zoom_out(self):
        self._apply_scale(1.0 / self._step)

    def reset_zoom(self):
        self.setTransform(QTransform())
        self._current_scale = 1.0
