# myLib/myGui/zoomable_view.py
from enum import Enum
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QTransform, QKeySequence, QShortcut, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget


class FitMode(str, Enum):
    NONE = "none"        # 不自動配適
    CONTAIN = "contain"  # 等比：整個內容都可見
    COVER = "cover"      # 不等比：填滿寬高（可能變形）
    WIDTH = "width"      # 依寬度貼齊
    HEIGHT = "height"    # 依高度貼齊

class ZoomableView(QGraphicsView):
    def __init__(self, widget: QWidget, parent=None,
                 min_scale=0.6, max_scale=3.0, step=1.12, start_scale=1.0):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self._proxy: QGraphicsProxyWidget = self.scene().addWidget(widget)

        self.setRenderHints(self.renderHints() | QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)

        self._min_scale = float(min_scale)
        self._max_scale = float(max_scale)
        self._step = float(step)
        self._current_scale = 1.0

        self._fit_mode: FitMode = FitMode.NONE  # ← 預設不自動配適

        QShortcut(QKeySequence("Ctrl+="), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.reset_zoom)

        self._fit_initial()
        if abs(float(start_scale) - 1.0) > 1e-6:
            self.set_zoom(start_scale)

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

    def set_fit_mode(self, mode: str | FitMode):
        self._fit_mode = FitMode(mode)
        self._apply_fit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_fit()

    def _apply_fit(self):
        if self._fit_mode == FitMode.NONE:
            return
        rect: QRectF = self._proxy.sceneBoundingRect()
        if rect.isEmpty():
            return

        vw = max(1, self.viewport().width())
        vh = max(1, self.viewport().height())
        sw = rect.width()
        sh = rect.height()

        if self._fit_mode == FitMode.CONTAIN:
            s = min(vw / sw, vh / sh)
            self.set_zoom(s)
        elif self._fit_mode == FitMode.COVER:
            # 不等比填滿：設定非等比縮放（可能變形）
            sx = vw / sw
            sy = vh / sh
            self.setTransform(QTransform())  # 先清空
            self._current_scale = 1.0
            self.scale(sx, sy)
        elif self._fit_mode == FitMode.WIDTH:
            s = vw / sw
            self.set_zoom(s)
        elif self._fit_mode == FitMode.HEIGHT:
            s = vh / sh
            self.set_zoom(s)

    def set_zoom(self, scale: float):
        s = max(self._min_scale, min(self._max_scale, float(scale)))
        self.setTransform(QTransform())
        self._current_scale = 1.0
        self._apply_scale(s)
