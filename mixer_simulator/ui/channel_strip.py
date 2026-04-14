# mixer_simulator/ui/channel_strip.py
# 推子条部件 - 整合LCD、编码器、推子、4个按钮

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from mixer_simulator.ui.lcd_widget import LcdWidget
from mixer_simulator.ui.encoder_widget import EncoderWidget
from mixer_simulator.ui.button_widget import ButtonWidget
from mixer_simulator.ui.fader_widget import FaderWidget, midi_to_db
from mixer_simulator.ui.style import BG_CHANNEL, BORDER_COLOR, TEXT_SECONDARY
from mixer_simulator.core.controller import ChannelState, ENCODER_MODES


class ChannelStrip(QWidget):
    """单条推子条 - strip_id 为物理编号（0~4）"""

    # 推子条发出的信号
    fader_moved = pyqtSignal(int, int)           # strip_id, value
    encoder_rotated = pyqtSignal(int, float)     # strip_id, delta（含加速）
    encoder_single_clicked = pyqtSignal(int)     # strip_id
    encoder_double_clicked = pyqtSignal(int)     # strip_id
    mute_clicked = pyqtSignal(int)               # strip_id
    solo_clicked = pyqtSignal(int)               # strip_id
    select_clicked = pyqtSignal(int)             # strip_id
    dyn_clicked = pyqtSignal(int)                # strip_id

    def __init__(self, strip_id: int, parent=None):
        super().__init__(parent)
        self.strip_id = strip_id
        self._current_channel = 1
        self._encoder_mode = "COMP"
        self._page_turn_mode = False

        self.setFixedWidth(165)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """构建推子条布局：LCD → 编码器+上方2按钮 → 推子 → 下方2按钮"""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(4)

        # 通道标题标签
        self._title_label = QLabel(f"Strip {self.strip_id + 1}", self)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9px;")
        outer.addWidget(self._title_label)

        # LCD
        self._lcd = LcdWidget(self)
        outer.addWidget(self._lcd, alignment=Qt.AlignmentFlag.AlignCenter)

        # 编码器行（编码器居中，左右各一个按钮）
        enc_row = QHBoxLayout()
        enc_row.setSpacing(4)
        self._btn_mute = ButtonWidget("MUTE", self)
        self._encoder = EncoderWidget(self)
        self._btn_solo = ButtonWidget("SOLO", self)
        enc_row.addWidget(self._btn_mute)
        enc_row.addWidget(self._encoder)
        enc_row.addWidget(self._btn_solo)
        outer.addLayout(enc_row)

        # 推子
        self._fader = FaderWidget(self)
        outer.addWidget(self._fader, alignment=Qt.AlignmentFlag.AlignCenter)

        # 下方按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        self._btn_select = ButtonWidget("SELECT", self)
        self._btn_dyn = ButtonWidget("DYN", self)
        btn_row.addWidget(self._btn_select)
        btn_row.addWidget(self._btn_dyn)
        outer.addLayout(btn_row)

        # 连接内部信号
        self._fader.value_changed.connect(self._on_fader_moved)
        self._fader.calibration_progress.connect(self._on_cal_progress)
        self._fader.calibration_complete.connect(self._on_cal_complete)
        self._encoder.rotated.connect(self._on_encoder_rotated)
        self._encoder.single_clicked.connect(self._on_encoder_single_click)
        self._encoder.double_clicked.connect(self._on_encoder_double_click)
        self._btn_mute.clicked.connect(lambda: self.mute_clicked.emit(self.strip_id))
        self._btn_solo.clicked.connect(lambda: self.solo_clicked.emit(self.strip_id))
        self._btn_select.clicked.connect(lambda: self.select_clicked.emit(self.strip_id))
        self._btn_dyn.clicked.connect(lambda: self.dyn_clicked.emit(self.strip_id))

    def _apply_style(self):
        """应用推子条样式"""
        self.setStyleSheet(
            f"ChannelStrip {{ background-color: {BG_CHANNEL}; "
            f"border: 1px solid {BORDER_COLOR}; border-radius: 6px; }}"
        )

    # ------------------------------------------------------------------ #
    # 公开接口：从控制器更新UI
    # ------------------------------------------------------------------ #

    def set_current_channel(self, ch_num: int, ch_name: str):
        """更新当前显示的通道号和名称"""
        self._current_channel = ch_num
        self._title_label.setText(f"CH{ch_num}")
        self._lcd.set_channel(ch_num, ch_name)

    def update_from_channel_state(self, ch_state: ChannelState):
        """从通道状态对象恢复所有UI"""
        mode_name = ENCODER_MODES[ch_state.encoder_mode_index]
        self._encoder_mode = mode_name
        self._encoder.set_mode(mode_name)

        # 更新LCD编码器显示
        val_str = self._get_encoder_value_str(ch_state)
        self._lcd.set_channel(ch_state.ch_num, ch_state.channel_name)
        self._lcd.set_encoder_display(mode_name, val_str)
        self._lcd.set_button_states(
            ch_state.mute_active,
            ch_state.solo_active,
            ch_state.select_active,
            ch_state.dyn_active,
        )
        self._lcd.set_fader_db(midi_to_db(ch_state.fader_value))

        # 更新按钮状态
        self._btn_mute.set_active(ch_state.mute_active)
        self._btn_solo.set_active(ch_state.solo_active)
        self._btn_select.set_active(ch_state.select_active)
        self._btn_dyn.set_active(ch_state.dyn_active)

        # 更新推子（不发送信号，避免循环）
        self._fader.set_value(ch_state.fader_value, emit=False)
        self._title_label.setText(f"CH{ch_state.ch_num}")

    def start_channel_calibration(self, target_val: int, ch_num: int, ch_name: str):
        """开始推子校准动画并显示校准LCD"""
        self._lcd.set_calibrating(True, 0, ch_num, ch_name)
        self._fader.start_calibration(target_val)

    def set_page_turn_mode(self, active: bool, target_ch: int):
        """设置翻页模式显示"""
        self._page_turn_mode = active
        self._encoder.set_page_turn_mode(active)
        self._lcd.set_page_turn_mode(active, target_ch)

    def update_encoder_display(self, mode: str, val_str: str):
        """更新编码器模式显示"""
        self._encoder_mode = mode
        self._encoder.set_mode(mode)
        self._lcd.set_encoder_display(mode, val_str)

    def update_button_state(self, btn_type: str, active: bool):
        """更新单个按钮状态"""
        if btn_type == "MUTE":
            self._btn_mute.set_active(active)
            self._lcd.set_mute_active(active)
        elif btn_type == "SOLO":
            self._btn_solo.set_active(active)
        elif btn_type == "SELECT":
            self._btn_select.set_active(active)
        elif btn_type == "DYN":
            self._btn_dyn.set_active(active)

        # 刷新LCD按钮提示行
        self._lcd.set_button_states(
            self._btn_mute.is_active(),
            self._btn_solo.is_active(),
            self._btn_select.is_active(),
            self._btn_dyn.is_active(),
        )

    # ------------------------------------------------------------------ #
    # 内部信号转发
    # ------------------------------------------------------------------ #

    def _on_fader_moved(self, val: int):
        self._lcd.set_fader_db(midi_to_db(val))
        self.fader_moved.emit(self.strip_id, val)

    def _on_cal_progress(self, pct: int):
        self._lcd.set_calibrating(
            True, pct,
            self._current_channel,
            self._lcd._ch_name
        )

    def _on_cal_complete(self):
        self._lcd.set_calibrating(False, 100, self._current_channel, "")

    def _on_encoder_rotated(self, delta: float):
        self.encoder_rotated.emit(self.strip_id, delta)

    def _on_encoder_single_click(self):
        self.encoder_single_clicked.emit(self.strip_id)

    def _on_encoder_double_click(self):
        self.encoder_double_clicked.emit(self.strip_id)

    # ------------------------------------------------------------------ #
    # 辅助
    # ------------------------------------------------------------------ #

    def _get_encoder_value_str(self, ch_state: ChannelState) -> str:
        """根据编码器模式获取参数值字符串"""
        idx = ch_state.encoder_mode_index
        if idx == 0:
            return f"{ch_state.comp_thr:.1f}dB"
        elif idx == 1:
            return f"{ch_state.gate_thr:.1f}dB"
        else:
            pan = ch_state.pan
            if pan < 0:
                return f"L{abs(pan)}"
            elif pan > 0:
                return f"R{pan}"
            return "C"
