# ui/encoder_widget.py
# 编码器控件 - 模拟EC11旋转编码器（旋转+点击+WS2812B LED）

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent, QWheelEvent

import math

from .style import (
    ENCODER_BG, ENCODER_DOT,
    LED_OFF, LED_WHITE, LED_CYAN, LED_YELLOW,
    TEXT_LABEL
)


class EncoderKnob(QWidget):
    """编码器旋钮绘制控件"""

    rotated = pyqtSignal(int)   # 旋转信号 delta=+1/-1
    clicked = pyqtSignal()      # 点击信号

    KNOB_SIZE = 56  # 旋钮直径

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0          # 当前角度（度），0=正上方
        self._last_mouse_y = 0     # 上次鼠标Y坐标（用于拖动旋转）
        self._dragging = False
        self.setFixedSize(self.KNOB_SIZE, self.KNOB_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("左键拖动旋转 / 滚轮调节 / 双击重置")

    def set_angle(self, angle: float):
        """设置旋钮角度"""
        self._angle = angle % 360
        self.update()

    def rotate_by(self, delta_angle: float):
        """旋转指定角度"""
        self._angle = (self._angle + delta_angle) % 360
        self.update()

    def paintEvent(self, event):
        """绘制编码器旋钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2
        r = min(w, h) // 2 - 2  # 旋钮半径

        # 绘制外圈阴影
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#111111")))
        painter.drawEllipse(QPoint(cx, cy), r + 2, r + 2)

        # 绘制旋钮主体（深灰色）
        painter.setBrush(QBrush(QColor(ENCODER_BG)))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawEllipse(QPoint(cx, cy), r, r)

        # 绘制内圈纹理线（装饰）
        painter.setPen(QPen(QColor("#3a3a3a"), 1))
        inner_r = int(r * 0.7)
        painter.drawEllipse(QPoint(cx, cy), inner_r, inner_r)

        # 绘制指示点（绿色小圆点，随旋转移动）
        angle_rad = math.radians(self._angle - 90)  # 从12点位置开始
        dot_r = int(r * 0.68)
        dot_x = cx + int(dot_r * math.cos(angle_rad))
        dot_y = cy + int(dot_r * math.sin(angle_rad))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(ENCODER_DOT)))
        painter.drawEllipse(QPoint(dot_x, dot_y), 4, 4)

        # 绘制中心小点
        painter.setBrush(QBrush(QColor("#555555")))
        painter.drawEllipse(QPoint(cx, cy), 3, 3)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下 - 记录起始位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_mouse_y = event.pos().y()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标拖动 - 旋转编码器"""
        if self._dragging:
            dy = self._last_mouse_y - event.pos().y()  # 上移=正，下移=负
            self._last_mouse_y = event.pos().y()
            if dy != 0:
                delta = 1 if dy > 0 else -1
                self.rotate_by(delta * 15)  # 每步旋转15度
                self.rotated.emit(delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击 = 编码器按键点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def wheelEvent(self, event: QWheelEvent):
        """滚轮旋转编码器"""
        delta = 1 if event.angleDelta().y() > 0 else -1
        self.rotate_by(delta * 15)
        self.rotated.emit(delta)


class LedIndicator(QWidget):
    """WS2812B LED指示灯模拟"""

    LED_SIZE = 12  # LED直径

    def __init__(self, color: str = LED_OFF, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(self.LED_SIZE, self.LED_SIZE)

    def set_color(self, color: str):
        """设置LED颜色"""
        self._color = color
        self.update()

    def paintEvent(self, event):
        """绘制LED"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2
        r = min(self.width(), self.height()) // 2 - 1

        # 熄灭状态
        if self._color == LED_OFF or self._color == "#1a1a1a":
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.setBrush(QBrush(QColor("#1a1a1a")))
            painter.drawEllipse(QPoint(cx, cy), r, r)
            return

        # 点亮状态 - 带发光效果
        led_color = QColor(self._color)

        # 外圈发光（半透明）
        glow_color = QColor(led_color)
        glow_color.setAlpha(60)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(QPoint(cx, cy), r + 2, r + 2)

        # LED主体
        painter.setPen(QPen(led_color.darker(150), 1))
        painter.setBrush(QBrush(led_color))
        painter.drawEllipse(QPoint(cx, cy), r, r)

        # 高光
        highlight = QColor(255, 255, 255, 100)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(QPoint(cx - 1, cy - 1), r // 3, r // 3)


class EncoderWidget(QWidget):
    """编码器控件 - 旋钮 + WS2812B LED + 标签
    
    布局（从上到下）：
      标签
      [旋钮]  [LED]
    """

    rotated = pyqtSignal(int)   # 旋转信号
    clicked = pyqtSignal()      # 点击信号

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self._setup_ui()
        # 默认LED为白色（激活状态）
        self.set_led_color(LED_WHITE)

    def _setup_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标签
        self.label = QLabel(f"ENC{self.channel_id + 1}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 10px; background: transparent;")
        layout.addWidget(self.label)

        # 旋钮 + LED 横向布局
        knob_led_layout = QHBoxLayout()
        knob_led_layout.setContentsMargins(0, 0, 0, 0)
        knob_led_layout.setSpacing(6)
        knob_led_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 旋钮
        self.knob = EncoderKnob()
        self.knob.rotated.connect(self._on_rotated)
        self.knob.clicked.connect(self._on_clicked)
        knob_led_layout.addWidget(self.knob)

        # LED指示灯（WS2812B）
        self.led = LedIndicator(LED_OFF)
        self.led.setToolTip("WS2812B LED\n白色=默认 青色=EQ 黄色=PAN")
        knob_led_layout.addWidget(self.led)

        layout.addLayout(knob_led_layout)

        # 编码器值标签
        self.value_label = QLabel("64")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        layout.addWidget(self.value_label)

    def _on_rotated(self, delta: int):
        """旋钮旋转事件"""
        self.rotated.emit(delta)

    def _on_clicked(self):
        """旋钮点击（双击）事件"""
        self.clicked.emit()

    def set_led_color(self, color: str):
        """设置LED颜色"""
        self.led.set_color(color)

    def set_value_display(self, value: int):
        """更新编码器值显示"""
        self.value_label.setText(str(value))

    def set_mode(self, mode: str):
        """根据编码器模式更新LED颜色"""
        from .style import LED_WHITE, LED_CYAN, LED_YELLOW
        color_map = {
            "VOL": LED_WHITE,
            "EQ": LED_CYAN,
            "PAN": LED_YELLOW,
        }
        self.set_led_color(color_map.get(mode, LED_WHITE))
