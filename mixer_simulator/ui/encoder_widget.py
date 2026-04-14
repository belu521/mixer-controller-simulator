# ui/encoder_widget.py
# 编码器控件 - 模拟EC11旋转编码器（旋转+单击+双击+WS2812B LED）
# 升级：单击切换模式、双击进入翻页、旋转加速度曲线

import math
import time

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QWheelEvent

from .style import (
    ENCODER_BG, ENCODER_DOT,
    LED_OFF, LED_WHITE, LED_CYAN, LED_YELLOW,
    TEXT_LABEL
)

# 编码器模式LED颜色
ENC_MODE_LED_COLORS = {
    0: '#00ffff',   # COMP - 青色
    1: '#ffffff',   # GATE - 白色
    2: '#ffff00',   # PAN  - 黄色
}
ENC_MODE_LABELS = {0: 'COMP', 1: 'GATE', 2: 'PAN'}

# 单击判定等待时间（ms）：在此时间内若第二次点击则判定为双击
CLICK_TIMEOUT_MS = 300


class EncoderKnob(QWidget):
    """编码器旋钮绘制控件
    
    交互方式：
      - 左键拖动 / 滚轮 → 旋转（rotated信号）
      - 单次点击（不拖动） → clicked 信号
      - 快速双击（两次点击间隔 < 300ms） → double_clicked 信号
    """

    rotated        = pyqtSignal(int)   # 旋转 delta=+1/-1（未含加速度）
    clicked        = pyqtSignal()      # 单击（模式切换）
    double_clicked = pyqtSignal()      # 双击（进入翻页）

    KNOB_SIZE = 56  # 旋钮直径（px）

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle      = 0.0       # 当前旋钮角度（度）
        self._last_y     = 0         # 上次鼠标Y（拖动用）
        self._dragging   = False
        self._did_drag   = False     # 本次按下是否发生了拖动

        # 单击延迟计时器（用于区分单/双击）
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._emit_single_click)

        self.setFixedSize(self.KNOB_SIZE, self.KNOB_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(
            "左键拖动 / 滚轮 → 旋转\n"
            "单击 → 切换模式\n"
            "双击 → 进入翻页"
        )

    def _emit_single_click(self):
        """定时器超时：确认为单击"""
        self.clicked.emit()

    def set_angle(self, angle: float):
        self._angle = angle % 360
        self.update()

    def rotate_by(self, delta_angle: float):
        self._angle = (self._angle + delta_angle) % 360
        self.update()

    # ---- 绘制 ----
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 2

        # 外圈阴影
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#111111")))
        painter.drawEllipse(QPoint(cx, cy), r + 2, r + 2)

        # 旋钮主体
        painter.setBrush(QBrush(QColor(ENCODER_BG)))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawEllipse(QPoint(cx, cy), r, r)

        # 内圈纹理线
        painter.setPen(QPen(QColor("#3a3a3a"), 1))
        inner_r = int(r * 0.7)
        painter.drawEllipse(QPoint(cx, cy), inner_r, inner_r)

        # 指示点（从12点位置开始随角度旋转）
        angle_rad = math.radians(self._angle - 90)
        dot_r = int(r * 0.68)
        dot_x = cx + int(dot_r * math.cos(angle_rad))
        dot_y = cy + int(dot_r * math.sin(angle_rad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(ENCODER_DOT)))
        painter.drawEllipse(QPoint(dot_x, dot_y), 4, 4)

        # 中心圆点
        painter.setBrush(QBrush(QColor("#555555")))
        painter.drawEllipse(QPoint(cx, cy), 3, 3)

    # ---- 鼠标事件 ----
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._did_drag = False
            self._last_y = event.pos().y()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            dy = self._last_y - event.pos().y()
            self._last_y = event.pos().y()
            if dy != 0:
                self._did_drag = True
                delta = 1 if dy > 0 else -1
                self.rotate_by(delta * 15)
                self.rotated.emit(delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._did_drag:
                # 无拖动的释放：启动单击计时器
                self._click_timer.start(CLICK_TIMEOUT_MS)
            self._dragging = False
            self._did_drag = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击：取消单击计时，改发双击信号"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_timer.stop()
            self.double_clicked.emit()

    def wheelEvent(self, event: QWheelEvent):
        delta = 1 if event.angleDelta().y() > 0 else -1
        self.rotate_by(delta * 15)
        self.rotated.emit(delta)


class LedIndicator(QWidget):
    """WS2812B LED指示灯模拟"""

    LED_SIZE = 12

    def __init__(self, color: str = LED_OFF, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(self.LED_SIZE, self.LED_SIZE)

    def set_color(self, color: str):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2
        r = min(self.width(), self.height()) // 2 - 1

        # 熄灭
        if self._color in (LED_OFF, "#1a1a1a"):
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.setBrush(QBrush(QColor("#1a1a1a")))
            painter.drawEllipse(QPoint(cx, cy), r, r)
            return

        # 点亮：主体 + 外圈发光 + 高光
        led_color = QColor(self._color)

        glow = QColor(led_color)
        glow.setAlpha(60)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPoint(cx, cy), r + 2, r + 2)

        painter.setPen(QPen(led_color.darker(150), 1))
        painter.setBrush(QBrush(led_color))
        painter.drawEllipse(QPoint(cx, cy), r, r)

        highlight = QColor(255, 255, 255, 100)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(QPoint(cx - 1, cy - 1), r // 3, r // 3)


class EncoderWidget(QWidget):
    """编码器控件 - EC11旋钮 + WS2812B LED
    
    新特性：
      - 单击（clicked）→ 循环切换3个模式（COMP / GATE / PAN）
      - 双击（double_clicked）→ 进入翻页通道选择
      - 旋转加速度曲线：间隔<100ms步进×6，100~300ms步进×3，>300ms步进×1
    """

    rotated        = pyqtSignal(int)   # 含加速度的旋转信号
    clicked        = pyqtSignal()      # 单击（模式切换）
    double_clicked = pyqtSignal()      # 双击（翻页入口）

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        # 初始化为当前时间，避免第一次旋转因间隔过大被判断为慢速
        self._last_rot_ms = time.monotonic() * 1000.0
        self._setup_ui()
        self.set_mode(0)          # 默认COMP模式，青色LED

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 模式标签
        self.label = QLabel("ENC:COMP")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 10px; background: transparent;")
        layout.addWidget(self.label)

        # 旋钮 + LED 横向布局
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.knob = EncoderKnob()
        self.knob.rotated.connect(self._on_rotated)
        self.knob.clicked.connect(self.clicked.emit)
        self.knob.double_clicked.connect(self.double_clicked.emit)
        row.addWidget(self.knob)

        self.led = LedIndicator(LED_OFF)
        self.led.setToolTip(
            "WS2812B LED\n青色=COMP  白色=GATE  黄色=PAN")
        row.addWidget(self.led)

        layout.addLayout(row)

        # 当前参数值标签
        self.value_label = QLabel("--")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        layout.addWidget(self.value_label)

    def _on_rotated(self, raw_delta: int):
        """旋转事件：应用加速度曲线后发出信号"""
        now_ms = time.monotonic() * 1000.0
        interval = now_ms - self._last_rot_ms
        self._last_rot_ms = now_ms

        # 加速度系数
        if interval < 100:
            step = 6    # 快速旋转
        elif interval < 300:
            step = 3    # 中速旋转
        else:
            step = 1    # 慢速旋转

        self.rotated.emit(raw_delta * step)

    def set_led_color(self, color: str):
        """直接设置LED颜色"""
        self.led.set_color(color)

    def set_value_display(self, text: str):
        """更新参数值标签"""
        self.value_label.setText(str(text))

    def set_mode(self, mode_idx: int):
        """根据模式索引更新LED颜色和标签
        
        mode_idx: 0=COMP（青色）, 1=GATE（白色）, 2=PAN（黄色）
        """
        color = ENC_MODE_LED_COLORS.get(mode_idx, LED_WHITE)
        label = ENC_MODE_LABELS.get(mode_idx, '??')
        self.led.set_color(color)
        self.label.setText(f"ENC:{label}")

