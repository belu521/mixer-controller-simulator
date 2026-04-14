# ui/channel_strip.py
# 单通道条控件 - 整合LCD + 编码器 + 按键 + 推子
# 升级：每列独立寻址（current_channel）、翻页模式、推子自动校准

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from .style import BG_CHANNEL, BORDER_COLOR, TEXT_LABEL, TEXT_PRIMARY
from .lcd_widget import LcdWidget
from .encoder_widget import EncoderWidget
from .button_widget import ButtonWidget, BTN_TYPE_MUTE, BTN_TYPE_SOLO, BTN_TYPE_DYN, BTN_TYPE_SEL
from .fader_widget import FaderWidget

# 向后兼容别名
BTN_TYPE_REC = BTN_TYPE_DYN


class ChannelStrip(QFrame):
    """单通道条控件 - 每列可独立映射到任意通道（1~144）
    
    PCB布局从上到下：
      1. 通道标题（CH N）
      2. LCD显示屏（4行）
      3. 编码器（旋钮+LED），支持单击/双击
      4. 上方按键区（MUTE + SOLO）
      5. 推子（垂直滑块，翻页后自动校准）
      6. 下方按键区（DYN + SEL）
    
    信号流：
      用户操作 → ChannelStrip信号 → MixerController处理 → 更新UI
    """

    # ---- 信号定义 ----
    fader_moved    = pyqtSignal(int, int)    # (col_idx, value)
    encoder_rotated = pyqtSignal(int, int)   # (col_idx, delta含加速度)
    encoder_clicked = pyqtSignal(int)        # (col_idx) 模式切换
    mute_clicked   = pyqtSignal(int)         # (col_idx)
    solo_clicked   = pyqtSignal(int)         # (col_idx)
    dyn_clicked    = pyqtSignal(int)         # (col_idx) DYN ON/OFF
    sel_clicked    = pyqtSignal(int)         # (col_idx)
    # 翻页确认：用户在bank模式选定通道后发出
    channel_change_requested = pyqtSignal(int, int)   # (col_idx, target_ch_num)

    # 向后兼容别名
    rec_clicked = dyn_clicked

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id            # 列索引 0~4
        self.current_channel = channel_id + 1   # 当前映射通道 1~144

        # ---- 翻页模式状态 ----
        self._bank_mode    = False
        self._bank_target  = self.current_channel

        # ---- 推子校准动画状态 ----
        self._calibrating    = False
        self._calib_target   = 100
        self._calib_start    = 100
        self._current_ch_name = f'CH{channel_id + 1}'

        self._calib_timer = QTimer(self)
        self._calib_timer.setInterval(50)    # 每50ms移动一步
        self._calib_timer.timeout.connect(self._calib_step)

        self._setup_ui()
        self._connect_signals()

    # ----------------------------------------------------------------
    # UI 初始化
    # ----------------------------------------------------------------
    def _setup_ui(self):
        self.setObjectName("channelStrip")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame#channelStrip {{
                background-color: {BG_CHANNEL};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
            }}
        """)
        self.setMinimumWidth(130)
        self.setMaximumWidth(165)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ---- 通道标题 ----
        self.ch_label = QLabel(f"CH {self.current_channel}")
        self.ch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ch_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            padding: 2px;
        """)
        layout.addWidget(self.ch_label)

        layout.addWidget(self._sep())

        # ---- 1. LCD显示屏 ----
        self.lcd = LcdWidget(self.channel_id)
        layout.addWidget(self.lcd, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ---- 2. 编码器 ----
        self.encoder = EncoderWidget(self.channel_id)
        layout.addWidget(self.encoder, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._sep())

        # ---- 3. 上方按键（MUTE + SOLO） ----
        upper_lbl = QLabel("上方按键")
        upper_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_lbl.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        layout.addWidget(upper_lbl)

        self.btn_mute = ButtonWidget(BTN_TYPE_MUTE)
        self.btn_mute.setToolTip(f"列{self.channel_id + 1} MUTE - 通道静音")
        layout.addWidget(self.btn_mute, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_solo = ButtonWidget(BTN_TYPE_SOLO)
        self.btn_solo.setToolTip(f"列{self.channel_id + 1} SOLO - 独奏监听")
        layout.addWidget(self.btn_solo, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._sep())

        # ---- 4. 推子 ----
        fader_lbl = QLabel("FADER")
        fader_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fader_lbl.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        layout.addWidget(fader_lbl)

        self.fader = FaderWidget(self.channel_id)
        layout.addWidget(self.fader, stretch=1,
                         alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._sep())

        # ---- 5. 下方按键（DYN + SEL） ----
        lower_lbl = QLabel("下方按键")
        lower_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lower_lbl.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        layout.addWidget(lower_lbl)

        self.btn_dyn = ButtonWidget(BTN_TYPE_DYN)
        self.btn_dyn.setToolTip(f"列{self.channel_id + 1} DYN - 动态处理总开关")
        layout.addWidget(self.btn_dyn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 向后兼容别名
        self.btn_rec = self.btn_dyn

        self.btn_sel = ButtonWidget(BTN_TYPE_SEL)
        self.btn_sel.setToolTip(f"列{self.channel_id + 1} SEL - 通道选择（单选）")
        layout.addWidget(self.btn_sel, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _sep(self) -> QFrame:
        """创建水平分割线"""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {BORDER_COLOR}; border: none;")
        return sep

    # ----------------------------------------------------------------
    # 信号连接
    # ----------------------------------------------------------------
    def _connect_signals(self):
        """连接控件信号（所有动作都先经过ChannelStrip过滤）"""
        # 推子：经过校准锁定过滤
        self.fader.value_changed.connect(self._on_fader_moved)

        # 编码器：根据模式（翻页/普通）路由
        self.encoder.rotated.connect(self._on_encoder_rotated)
        self.encoder.clicked.connect(self._on_encoder_clicked)
        self.encoder.double_clicked.connect(self._on_encoder_double_clicked)

        # 按键：直接透传（控制器处理Toggle逻辑）
        self.btn_mute.clicked.connect(lambda: self.mute_clicked.emit(self.channel_id))
        self.btn_solo.clicked.connect(lambda: self.solo_clicked.emit(self.channel_id))
        self.btn_dyn.clicked.connect(lambda: self.dyn_clicked.emit(self.channel_id))
        self.btn_sel.clicked.connect(lambda: self.sel_clicked.emit(self.channel_id))

    # ----------------------------------------------------------------
    # 事件过滤
    # ----------------------------------------------------------------
    def _on_fader_moved(self, value: int):
        """推子移动：校准期间不发出MIDI"""
        if not self._calibrating:
            self.fader_moved.emit(self.channel_id, value)

    def _on_encoder_rotated(self, delta: int):
        """编码器旋转（已含加速度）"""
        if self._calibrating:
            return
        if self._bank_mode:
            # 翻页模式：调整目标通道号
            self._bank_target = max(1, min(144, self._bank_target + delta))
            self.lcd.show_bank_mode(self._bank_target)
        else:
            self.encoder_rotated.emit(self.channel_id, delta)

    def _on_encoder_clicked(self):
        """编码器单击"""
        if self._calibrating:
            return
        if self._bank_mode:
            # 翻页模式：确认跳转
            self._bank_mode = False
            target = self._bank_target
            self.channel_change_requested.emit(self.channel_id, target)
        else:
            # 正常模式：切换编码器参数模式
            self.encoder_clicked.emit(self.channel_id)

    def _on_encoder_double_clicked(self):
        """编码器双击：进入翻页通道选择模式"""
        if self._calibrating:
            return
        self._bank_mode   = True
        self._bank_target = self.current_channel
        self.lcd.show_bank_mode(self._bank_target)

    # ----------------------------------------------------------------
    # 通道切换（由主窗口调用）
    # ----------------------------------------------------------------
    def switch_to_channel(self, ch_num: int, fader_value: int, ch_name: str,
                           enc_mode: int, comp_thr: float, gate_thr: float,
                           pan: int, mute: bool, solo: bool,
                           sel: bool, dyn: bool):
        """切换到新通道，开始推子校准动画
        
        参数全部来自新通道的 ChannelState。
        """
        self.current_channel  = ch_num
        self._current_ch_name = ch_name
        self._update_ch_label()

        # 更新按键LED状态
        self.btn_mute.set_active(mute)
        self.btn_solo.set_active(solo)
        self.btn_sel.set_active(sel)
        self.btn_dyn.set_active(dyn)

        # 更新编码器模式LED
        self.encoder.set_mode(enc_mode)

        # 更新LCD
        self.lcd.set_channel_info(ch_num, ch_name)
        self.lcd.set_encoder_state(enc_mode, comp_thr, gate_thr, pan)
        self.lcd.set_button_states(mute, solo, sel, dyn)

        # 启动推子校准
        self._calib_start  = self.fader.slider.value
        self._calib_target = fader_value
        self._calibrating  = True
        self.fader.slider._locked = True

        # 如果目标与当前一致，立即完成
        if self._calib_start == self._calib_target:
            self._finish_calibration()
        else:
            self.lcd.show_calibration(ch_num, ch_name, 0)
            self._calib_timer.start()

    # ----------------------------------------------------------------
    # 校准动画
    # ----------------------------------------------------------------
    def _calib_step(self):
        """每50ms推子向目标位置靠近一步"""
        current = self.fader.slider.value
        target  = self._calib_target
        diff    = target - current

        if abs(diff) <= 1:
            # 到达目标
            self.fader.slider.set_value(target)
            self._finish_calibration()
            return

        step    = max(1, abs(diff) // 4)
        new_val = current + (step if diff > 0 else -step)
        self.fader.slider.set_value(new_val)   # 会更新标签，但_calibrating=True所以不发MIDI

        # 进度百分比
        total = abs(self._calib_target - self._calib_start)
        if total == 0:
            progress = 100
        else:
            moved    = abs(new_val - self._calib_start)
            progress = min(99, int(moved / total * 100))
        self.lcd.show_calibration(
            self.current_channel, self._current_ch_name, progress)

    def _finish_calibration(self):
        """校准完成：解锁推子，恢复正常LCD显示"""
        self._calib_timer.stop()
        self._calibrating = False
        self.fader.slider._locked = False
        self.lcd.show_normal()

    # ----------------------------------------------------------------
    # 状态更新接口（由主窗口/控制器调用）
    # ----------------------------------------------------------------
    def _update_ch_label(self):
        """更新顶部通道标题"""
        self.ch_label.setText(f"CH {self.current_channel}")

    def update_from_channel_state(self, ch_num: int, ch_state) -> None:
        """根据通道状态对象更新全部UI（含LCD、按键LED、编码器LED）"""
        self.current_channel  = ch_num
        self._current_ch_name = ch_state.name
        self._update_ch_label()

        self.btn_mute.set_active(ch_state.mute)
        self.btn_solo.set_active(ch_state.solo)
        self.btn_sel.set_active(ch_state.select)
        self.btn_dyn.set_active(ch_state.dyn_on)
        self.encoder.set_mode(ch_state.enc_mode)

        self.lcd.set_channel_info(ch_num, ch_state.name)
        self.lcd.set_encoder_state(ch_state.enc_mode,
                                   ch_state.comp_thr,
                                   ch_state.gate_thr,
                                   ch_state.pan)
        self.lcd.set_button_states(ch_state.mute, ch_state.solo,
                                   ch_state.select, ch_state.dyn_on)

    def update_fader_db(self, db_str: str):
        """旧接口兼容：LCD电平由定时器维护，空实现"""
        pass

    def update_encoder_mode(self, mode_idx: int):
        """更新编码器模式（数字索引）"""
        self.encoder.set_mode(mode_idx)

    def update_encoder_value(self, value: int):
        """更新编码器参数值标签"""
        self.encoder.set_value_display(str(value))

    def update_button_state(self, btn_type: str, active: bool):
        """更新单个按键状态"""
        btn_map = {
            "mute": self.btn_mute,
            "solo": self.btn_solo,
            "dyn":  self.btn_dyn,
            "rec":  self.btn_dyn,   # 向后兼容
            "sel":  self.btn_sel,
        }
        btn = btn_map.get(btn_type)
        if btn:
            btn.set_active(active)


