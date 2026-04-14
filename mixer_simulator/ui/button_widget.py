# mixer_simulator/ui/button_widget.py
# 按钮部件 - MUTE/SOLO/SELECT/DYN，空白键帽 + LED指示

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont

from mixer_simulator.ui.style import (
    LED_OFF, LED_RED, LED_BLUE, LED_WHITE, LED_ORANGE,
    BG_PANEL, BORDER_COLOR, TEXT_LABEL
)

# 按钮类型 → LED颜色映射
BUTTON_COLORS = {
    "MUTE": LED_RED,
    "SOLO": LED_BLUE,
    "SELECT": LED_WHITE,
    "DYN": LED_ORANGE,
}


class ButtonWidget(QWidget):
    """单个按钮部件 - 包含空白键帽（圆角矩形）和LED指示点"""

    clicked = pyqtSignal()

    def __init__(self, btn_type: str, parent=None):
        super().__init__(parent)
        self._btn_type = btn_type
        self._active = False
        self._active_color = QColor(BUTTON_COLORS.get(btn_type, LED_WHITE))
        self._off_color = QColor(LED_OFF)

        self.setFixedSize(50, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(btn_type)

    def set_active(self, active: bool):
        """切换按钮激活状态"""
        self._active = active
        self.update()

    def is_active(self) -> bool:
        return self._active

    # ------------------------------------------------------------------ #
    # 绘制：顶部LED指示点 + 下方空白键帽
    # ------------------------------------------------------------------ #

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # LED 指示点（顶部小圆）
        led_r = 5
        led_x = w // 2
        led_y = 7
        led_color = self._active_color if self._active else self._off_color
        painter.setBrush(QBrush(led_color))
        painter.setPen(QPen(led_color.darker(150), 1))
        painter.drawEllipse(led_x - led_r, led_y - led_r, led_r * 2, led_r * 2)

        # 键帽（圆角矩形，空白无文字）
        cap_margin = 4
        cap_y = 16
        cap_h = h - cap_y - 4
        cap_color = QColor("#484848") if not self._active else QColor("#585858")
        painter.setBrush(QBrush(cap_color))
        painter.setPen(QPen(QColor(BORDER_COLOR), 1))
        painter.drawRoundedRect(cap_margin, cap_y, w - cap_margin * 2, cap_h, 4, 4)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
