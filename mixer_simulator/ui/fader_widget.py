# mixer_simulator/ui/fader_widget.py
# 推子部件 - 垂直推子 + 校准动画支持

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from mixer_simulator.ui.style import (
    FADER_TRACK, FADER_THUMB, BG_CHANNEL, TEXT_LABEL, TEXT_SECONDARY
)

# 推子校准动画步进定时器间隔（ms）
CALIBRATION_STEP_MS = 50
# 每步最大移动量（MIDI值单位）
CALIBRATION_MAX_STEP = 3


def midi_to_db(midi_val: int) -> str:
    """将MIDI值（0~127）转换为dB字符串"""
    if midi_val == 0:
        return "-∞dB"
    # 简单线性映射：127→0dB, 100→-10dB, 0→-∞
    db = (midi_val - 100) * 0.5
    return f"{db:+.1f}dB" if midi_val != 100 else "0.0dB"


class FaderSlider(QWidget):
    """自定义垂直推子滑块"""

    value_changed = pyqtSignal(int)          # 推子值变化（0~127）
    calibration_progress = pyqtSignal(int)   # 校准进度（0~100%）
    calibration_complete = pyqtSignal()      # 校准完成

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 200)

        self._value = 100         # 当前推子值（0~127）
        self._locked = False      # 是否处于锁定状态（校准中）
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_val = 0

        # 校准动画
        self._cal_target = 100
        self._cal_timer = QTimer(self)
        self._cal_timer.timeout.connect(self._calibration_step)

        self.setCursor(Qt.CursorShape.SizeVerCursor)

    @property
    def value(self) -> int:
        return self._value

    def set_value(self, val: int, emit: bool = True):
        """设置推子值（不触发动画）"""
        self._value = max(0, min(127, val))
        if emit:
            self.value_changed.emit(self._value)
        self.update()

    def start_calibration(self, target: int):
        """开始推子校准动画，平滑移动到目标值"""
        self._locked = True
        self._cal_target = max(0, min(127, target))
        self._cal_timer.start(CALIBRATION_STEP_MS)

    def _calibration_step(self):
        """校准动画步进"""
        diff = self._cal_target - self._value
        if abs(diff) <= CALIBRATION_MAX_STEP:
            self._value = self._cal_target
            self._cal_timer.stop()
            self._locked = False
            self.calibration_complete.emit()
            self.calibration_progress.emit(100)
        else:
            step = CALIBRATION_MAX_STEP if diff > 0 else -CALIBRATION_MAX_STEP
            self._value += step
            # 计算进度
            total = abs(self._cal_target - (self._value - step))
            done = abs(self._value - (self._value - step))
            if total > 0:
                pct = int(100 - abs(self._cal_target - self._value) / total * 100)
            else:
                pct = 100
            self.calibration_progress.emit(max(0, min(100, pct)))
        self.update()

    # ------------------------------------------------------------------ #
    # 绘制
    # ------------------------------------------------------------------ #

    def _value_to_y(self, val: int) -> int:
        """将推子值映射到Y坐标（值越大越靠上）"""
        h = self.height()
        margin = 14  # 顶部/底部留白
        return int(h - margin - (val / 127) * (h - margin * 2))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx = w // 2

        # 轨道
        track_w = 6
        margin = 14
        painter.setBrush(QBrush(QColor(FADER_TRACK)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(cx - track_w // 2, margin, track_w, h - margin * 2, 3, 3)

        # 刻度线（9个：-∞,-30,-20,-15,-10,-5,0,+5,+10）
        tick_values = [0, 20, 40, 55, 70, 85, 100, 112, 127]
        painter.setPen(QPen(QColor("#555555"), 1))
        for tv in tick_values:
            ty = self._value_to_y(tv)
            painter.drawLine(cx - 10, ty, cx - track_w // 2 - 1, ty)

        # 推子手柄
        thumb_y = self._value_to_y(self._value)
        thumb_h = 24
        thumb_w = 26
        thumb_color = QColor("#888888") if self._locked else QColor(FADER_THUMB)
        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawRoundedRect(
            cx - thumb_w // 2, thumb_y - thumb_h // 2,
            thumb_w, thumb_h, 4, 4
        )

        # 手柄中心线
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawLine(
            cx - thumb_w // 2 + 4, thumb_y,
            cx + thumb_w // 2 - 4, thumb_y
        )

        painter.end()

    # ------------------------------------------------------------------ #
    # 鼠标交互
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event):
        if self._locked:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_y = event.position().y()
            self._drag_start_val = self._value

    def mouseMoveEvent(self, event):
        if not self._dragging or self._locked:
            return
        h = self.height()
        margin = 14
        dy = self._drag_start_y - event.position().y()
        delta_val = int(dy / (h - margin * 2) * 127)
        new_val = max(0, min(127, self._drag_start_val + delta_val))
        self._value = new_val
        self.value_changed.emit(self._value)
        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = False


class FaderWidget(QWidget):
    """推子部件 = 滑块 + 标签"""

    value_changed = pyqtSignal(int)
    calibration_progress = pyqtSignal(int)
    calibration_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # 推子滑块
        self._slider = FaderSlider(self)
        layout.addWidget(self._slider, alignment=Qt.AlignmentFlag.AlignCenter)

        # 连接信号
        self._slider.value_changed.connect(self.value_changed)
        self._slider.calibration_progress.connect(self.calibration_progress)
        self._slider.calibration_complete.connect(self.calibration_complete)

    def get_value(self) -> int:
        return self._slider.value

    def set_value(self, val: int, emit: bool = True):
        self._slider.set_value(val, emit)

    def start_calibration(self, target: int):
        self._slider.start_calibration(target)

    def get_db_str(self) -> str:
        return midi_to_db(self._slider.value)
