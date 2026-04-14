# mixer_simulator/ui/encoder_widget.py
# 编码器旋钮部件 - 支持旋转、单击（切换模式）、双击（翻页模式）和加速

import time
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent

from mixer_simulator.ui.style import (
    ENCODER_BG, LED_OFF, LED_CYAN, LED_YELLOW, LED_WHITE, LED_GREEN
)

# 双击判定时间窗口（ms）
DOUBLE_CLICK_INTERVAL = 250

# 旋转加速阈值
FAST_INTERVAL_MS = 100    # 快速旋转：间隔<100ms
SLOW_INTERVAL_MS = 300    # 慢速旋转：间隔>300ms


class EncoderKnob(QWidget):
    """编码器旋钮 - 鼠标拖拽旋转，单击切换模式，双击翻页"""

    rotated = pyqtSignal(float)       # 旋转信号（含加速的步长）
    single_clicked = pyqtSignal()     # 单击信号
    double_clicked = pyqtSignal()     # 双击信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._angle = -135.0           # 当前旋转角度（用于绘制指示线）
        self._last_mouse_y = 0         # 上次鼠标Y坐标（用于拖拽）
        self._dragging = False         # 是否正在拖拽
        self._drag_threshold = 4       # 判定为拖拽的最小移动距离（像素）
        self._drag_accumulated = 0     # 累积拖拽距离

        # 单击/双击判定
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._on_click_timer)
        self._pending_click = False    # 是否有待定的单击

        # 旋转加速
        self._last_rotate_time = 0.0  # 上次旋转时间戳（秒）

        # 模式颜色
        self._led_color = QColor(LED_CYAN)

    def set_led_color(self, color_str: str):
        """设置指示点颜色"""
        self._led_color = QColor(color_str)
        self.update()

    # ------------------------------------------------------------------ #
    # 绘制
    # ------------------------------------------------------------------ #

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 3

        # 外圆背景
        painter.setBrush(QBrush(QColor(ENCODER_BG)))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # 指示线（从圆心指向边缘）
        angle_rad = math.radians(self._angle)
        line_r = r - 4
        lx = cx + line_r * math.sin(angle_rad)
        ly = cy - line_r * math.cos(angle_rad)
        painter.setPen(QPen(self._led_color, 2))
        painter.drawLine(int(cx), int(cy), int(lx), int(ly))

        # 指示点（旋钮末端小圆）
        dot_r = 4
        painter.setBrush(QBrush(self._led_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(lx) - dot_r, int(ly) - dot_r, dot_r * 2, dot_r * 2)

        painter.end()

    # ------------------------------------------------------------------ #
    # 鼠标事件
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._last_mouse_y = event.position().y()
            self._drag_accumulated = 0
            self._dragging = False

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            dy = self._last_mouse_y - event.position().y()  # 上移为正
            self._drag_accumulated += dy
            self._last_mouse_y = event.position().y()

            # 判定为拖拽
            if abs(self._drag_accumulated) >= self._drag_threshold:
                self._dragging = True
                steps_raw = self._drag_accumulated / self._drag_threshold
                self._drag_accumulated = 0

                # 计算加速步长
                step = self._calc_step(steps_raw)

                # 更新旋钮角度（仅用于视觉）
                self._angle = (self._angle + step * 5) % 360
                self.update()

                self.rotated.emit(step)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._dragging:
                # 没有拖拽 → 判定为点击
                if self._pending_click:
                    # 已有一次待定单击 → 双击
                    self._click_timer.stop()
                    self._pending_click = False
                    self.double_clicked.emit()
                else:
                    self._pending_click = True
                    self._click_timer.start(DOUBLE_CLICK_INTERVAL)
            self._dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        # Qt 的 doubleClickEvent 在 release 后触发，
        # 我们已在 mouseReleaseEvent 中处理双击逻辑，此处忽略
        pass

    def _on_click_timer(self):
        """单击定时器触发 → 确认为单击"""
        self._pending_click = False
        self.single_clicked.emit()

    def _calc_step(self, steps_raw: float) -> float:
        """根据旋转间隔计算加速步长"""
        now = time.monotonic()
        interval_ms = (now - self._last_rotate_time) * 1000
        self._last_rotate_time = now

        if interval_ms < FAST_INTERVAL_MS:
            multiplier = 6.0    # 快速旋转：大步长
        elif interval_ms > SLOW_INTERVAL_MS:
            multiplier = 1.0    # 慢速旋转：小步长
        else:
            # 线性插值
            t = (interval_ms - FAST_INTERVAL_MS) / (SLOW_INTERVAL_MS - FAST_INTERVAL_MS)
            multiplier = 6.0 - t * 5.0

        return steps_raw * multiplier


class EncoderWidget(QWidget):
    """编码器部件 = 旋钮 + LED指示"""

    rotated = pyqtSignal(float)
    single_clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    # 模式 → LED颜色映射
    MODE_COLORS = {
        "COMP": LED_CYAN,
        "GATE": LED_WHITE,
        "PAN": LED_YELLOW,
        "PAGE": LED_GREEN,  # 翻页模式
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = "COMP"
        self._page_turn = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._knob = EncoderKnob(self)
        layout.addWidget(self._knob, alignment=Qt.AlignmentFlag.AlignCenter)

        # 连接信号
        self._knob.rotated.connect(self.rotated)
        self._knob.single_clicked.connect(self.single_clicked)
        self._knob.double_clicked.connect(self.double_clicked)

        self._update_led()

    def set_mode(self, mode: str):
        """设置模式颜色（COMP/GATE/PAN）"""
        self._current_mode = mode
        if not self._page_turn:
            self._update_led()

    def set_page_turn_mode(self, active: bool):
        """翻页模式：绿色LED"""
        self._page_turn = active
        self._update_led()

    def _update_led(self):
        key = "PAGE" if self._page_turn else self._current_mode
        color = self.MODE_COLORS.get(key, LED_WHITE)
        self._knob.set_led_color(color)
