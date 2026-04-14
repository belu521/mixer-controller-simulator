# ui/fader_widget.py
# 推子控件 - 模拟RSA0N11M9A0J 100mm电动推子

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint, QRect, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QMouseEvent, QWheelEvent, QFont
)

from .style import FADER_TRACK, FADER_THUMB, BG_PANEL, TEXT_LABEL, BORDER_COLOR
from ..core.controller import midi_to_db


class FaderSlider(QWidget):
    """推子滑动条绘制控件（垂直）
    
    - 鼠标拖动改变值
    - 双击归位到100（0dB）
    - 右键归位到127（最大值）
    - 滚轮微调
    """

    value_changed = pyqtSignal(int)  # 值变化信号 (midi_value 0-127)

    TRACK_WIDTH = 8       # 轨道宽度
    THUMB_WIDTH = 34      # 推子手柄宽度
    THUMB_HEIGHT = 16     # 推子手柄高度

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 100          # 当前MIDI值 (0-127)
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_value = 0
        self._locked = False       # 锁定标志（校准动画期间锁定鼠标操作）

        # 电机归位动画
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)  # ~60fps
        self._anim_timer.timeout.connect(self._anim_step)
        self._anim_target = 0

        self.setMinimumSize(50, 200)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(50)
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        self.setToolTip("拖动调节 | 双击归位0dB(MIDI=100) | 右键归位最大(MIDI=127) | 滚轮微调")

    @property
    def value(self) -> int:
        """当前MIDI值"""
        return self._value

    def _value_to_y(self, value: int) -> int:
        """将MIDI值转换为Y坐标（像素）"""
        h = self.height()
        thumb_half = self.THUMB_HEIGHT // 2
        usable_h = h - 2 * thumb_half
        # 值127=顶部（小Y），值0=底部（大Y）
        return thumb_half + int((1.0 - value / 127.0) * usable_h)

    def _y_to_value(self, y: int) -> int:
        """将Y坐标转换为MIDI值"""
        h = self.height()
        thumb_half = self.THUMB_HEIGHT // 2
        usable_h = h - 2 * thumb_half
        if usable_h <= 0:
            return 0
        ratio = 1.0 - (y - thumb_half) / usable_h
        return max(0, min(127, int(ratio * 127)))

    def set_value(self, value: int, emit_signal: bool = True):
        """设置推子值"""
        value = max(0, min(127, value))
        if value != self._value:
            self._value = value
            self.update()
            if emit_signal:
                self.value_changed.emit(value)

    def _start_animation(self, target: int):
        """启动电机归位动画"""
        self._anim_target = target
        if not self._anim_timer.isActive():
            self._anim_timer.start()

    def _anim_step(self):
        """动画步进"""
        diff = self._anim_target - self._value
        if abs(diff) <= 2:
            self.set_value(self._anim_target)
            self._anim_timer.stop()
        else:
            # 缓动效果
            step = max(1, abs(diff) // 4)
            new_val = self._value + (step if diff > 0 else -step)
            self.set_value(new_val)

    def paintEvent(self, event):
        """绘制推子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2
        thumb_y = self._value_to_y(self._value)
        thumb_half = self.THUMB_HEIGHT // 2

        # ---- 绘制轨道 ----
        track_x = cx - self.TRACK_WIDTH // 2
        track_top = thumb_half
        track_bottom = h - thumb_half

        # 轨道背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(FADER_TRACK)))
        painter.drawRoundedRect(track_x, track_top,
                                self.TRACK_WIDTH, track_bottom - track_top,
                                3, 3)

        # 轨道填充（当前位置以下）- 蓝色高亮
        fill_top = thumb_y
        fill_height = track_bottom - thumb_y
        if fill_height > 0:
            gradient = QLinearGradient(0, fill_top, 0, track_bottom)
            gradient.setColorAt(0, QColor("#3399ff"))
            gradient.setColorAt(1, QColor("#1166cc"))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(track_x, fill_top,
                                    self.TRACK_WIDTH, fill_height,
                                    3, 3)

        # 0dB刻度线（MIDI=100位置）
        mark_y = self._value_to_y(100)
        painter.setPen(QPen(QColor("#ff8800"), 1))
        painter.drawLine(track_x - 4, mark_y, track_x + self.TRACK_WIDTH + 4, mark_y)

        # ---- 绘制推子手柄 ----
        thumb_x = cx - self.THUMB_WIDTH // 2
        thumb_rect = QRect(thumb_x, thumb_y - thumb_half,
                           self.THUMB_WIDTH, self.THUMB_HEIGHT)

        # 手柄渐变
        gradient = QLinearGradient(thumb_x, thumb_y - thumb_half,
                                   thumb_x, thumb_y + thumb_half)
        gradient.setColorAt(0, QColor("#d0d0d0"))
        gradient.setColorAt(0.4, QColor(FADER_THUMB))
        gradient.setColorAt(0.6, QColor(FADER_THUMB))
        gradient.setColorAt(1, QColor("#888888"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawRoundedRect(thumb_rect, 3, 3)

        # 手柄中间刻度线
        painter.setPen(QPen(QColor("#555555"), 1))
        line_x1 = thumb_x + 5
        line_x2 = thumb_x + self.THUMB_WIDTH - 5
        for dy in [-2, 0, 2]:
            painter.drawLine(line_x1, thumb_y + dy, line_x2, thumb_y + dy)

        # ---- 刻度标记（左侧） ----
        painter.setPen(QPen(QColor("#666666"), 1))
        tick_x = track_x - 8
        for tick_val in [127, 100, 75, 50, 25, 0]:
            ty = self._value_to_y(tick_val)
            painter.drawLine(tick_x, ty, tick_x + 4, ty)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下"""
        if self._locked:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._anim_timer.stop()
            self._dragging = True
            self._drag_start_y = event.pos().y()
            self._drag_start_value = self._value
            # 直接跳转到点击位置
            self.set_value(self._y_to_value(event.pos().y()))
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键 → 电机归位到127（最大值）
            self._start_animation(127)

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标拖动"""
        if self._dragging:
            self.set_value(self._y_to_value(event.pos().y()))

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击 → 电机归位到0dB（MIDI=100）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_animation(100)

    def wheelEvent(self, event: QWheelEvent):
        """滚轮微调"""
        delta = 1 if event.angleDelta().y() > 0 else -1
        self.set_value(self._value + delta)


class FaderWidget(QWidget):
    """推子控件 - 包含推子滑块 + 值显示标签
    
    布局（从上到下）：
      MIDI值标签
      [推子滑块]
      dB值标签
      通道标签
    """

    value_changed = pyqtSignal(int)  # 值变化信号

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self._setup_ui()

    def _setup_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # MIDI值标签（顶部）
        self.midi_label = QLabel("100")
        self.midi_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.midi_label.setStyleSheet(f"color: #88aacc; font-size: 11px; font-weight: bold; background: transparent;")
        self.midi_label.setFixedHeight(18)
        layout.addWidget(self.midi_label)

        # 推子滑块
        self.slider = FaderSlider()
        self.slider.value_changed.connect(self._on_value_changed)
        layout.addWidget(self.slider, stretch=1)

        # dB值标签（底部）
        self.db_label = QLabel("0.0 dB")
        self.db_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.db_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 10px; background: transparent;")
        self.db_label.setFixedHeight(16)
        layout.addWidget(self.db_label)

    def _on_value_changed(self, value: int):
        """推子值变化处理"""
        db_str = midi_to_db(value)
        self.midi_label.setText(str(value))
        if db_str == "-inf":
            self.db_label.setText("-inf dB")
        else:
            try:
                db_val = float(db_str)
                self.db_label.setText(f"{db_val:+.1f} dB")
            except ValueError:
                self.db_label.setText(f"{db_str} dB")
        self.value_changed.emit(value)

    def set_value(self, value: int):
        """外部设置推子值"""
        self.slider.set_value(value)

    @property
    def value(self) -> int:
        """当前MIDI值"""
        return self.slider.value
