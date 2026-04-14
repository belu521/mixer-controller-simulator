# core/controller.py
# 核心控制器逻辑 - 支持144通道状态管理（雅马哈DM系列）

from PyQt6.QtCore import QObject, pyqtSignal

# ---- 编码器模式定义 ----
ENC_MODE_COMP = 0   # 压缩器阈值模式
ENC_MODE_GATE = 1   # 噪声门阈值模式
ENC_MODE_PAN  = 2   # 声像模式

ENC_MODE_NAMES  = ["COMP", "GATE", "PAN"]
ENC_MODE_COLORS = ["#00ffff", "#ffffff", "#ffff00"]  # 青色 / 白色 / 黄色

# 最大通道数（DM7支持144个输入通道）
MAX_CHANNELS = 144

# MIDI CC编号（雅马哈DM系列）
CC_FADER_VOLUME = 7    # 推子音量
CC_GATE_THR     = 16   # 噪声门阈值
CC_COMP_THR     = 18   # 压缩器阈值
CC_PAN          = 10   # 声像

# MIDI CC到dB换算基准
MIDI_0DB_VALUE = 100   # MIDI值100 = 0 dB
MIDI_MAX_VALUE = 127   # MIDI值127 = +6 dB


def midi_to_db(midi_value: int) -> str:
    """将MIDI值(0-127)转换为dB字符串显示"""
    if midi_value == 0:
        return "-inf"
    elif midi_value <= MIDI_0DB_VALUE:
        db = (midi_value / MIDI_0DB_VALUE) * 60.0 - 60.0
        return f"{db:.1f}"
    else:
        db = ((midi_value - MIDI_0DB_VALUE) / (MIDI_MAX_VALUE - MIDI_0DB_VALUE)) * 6.0
        return f"+{db:.1f}"


def comp_thr_to_midi(thr_db: float) -> int:
    """COMP THR dB值(-60~0)转MIDI值(0~127)"""
    ratio = (thr_db + 60.0) / 60.0
    return max(0, min(127, int(ratio * 127)))


def gate_thr_to_midi(thr_db: float) -> int:
    """GATE THR dB值(-80~0)转MIDI值(0~127)"""
    ratio = (thr_db + 80.0) / 80.0
    return max(0, min(127, int(ratio * 127)))


def pan_to_midi(pan: int) -> int:
    """PAN值(-63~63)转MIDI值(0~127), 0=中央64"""
    return max(0, min(127, pan + 64))


class ChannelState:
    """单通道状态（支持1~144个通道）"""

    def __init__(self, ch_num: int):
        self.fader: int       = 100          # 推子MIDI值 0~127（100 = 0dB）
        self.mute: bool       = False
        self.solo: bool       = False
        self.select: bool     = False
        self.dyn_on: bool     = False        # 动态处理总开关
        self.comp_thr: float  = -20.0        # 压缩器阈值 dB, -60~0
        self.gate_thr: float  = -40.0        # 噪声门阈值 dB, -80~0
        self.pan: int         = 0            # 声像 -63~63
        self.name: str        = f"CH{ch_num}"  # 通道名
        self.enc_mode: int    = ENC_MODE_COMP  # 编码器模式

    @property
    def fader_db(self) -> str:
        """推子dB值字符串"""
        return midi_to_db(self.fader)

    @property
    def enc_param_str(self) -> str:
        """编码器当前参数显示字符串"""
        if self.enc_mode == ENC_MODE_COMP:
            return f"COMP THR{self.comp_thr:+.0f}dB"
        elif self.enc_mode == ENC_MODE_GATE:
            return f"GATE THR{self.gate_thr:+.0f}dB"
        else:
            if self.pan == 0:
                pan_str = "C"
            elif self.pan < 0:
                pan_str = f"L{abs(self.pan)}"
            else:
                pan_str = f"R{self.pan}"
            return f"PAN      {pan_str:>4}"


class MixerController(QObject):
    """混音控制器核心逻辑 - 管理最多144个通道，5列独立寻址"""

    # ---- 信号定义 ----
    fader_changed           = pyqtSignal(int, int)        # (col_idx, midi_value)
    encoder_changed         = pyqtSignal(int, int)        # (col_idx, midi_value)
    encoder_mode_changed    = pyqtSignal(int, int)        # (col_idx, mode_index)
    button_changed          = pyqtSignal(int, str, bool)  # (col_idx, btn_type, state)
    midi_message_sent       = pyqtSignal(str)             # MIDI日志消息
    channel_assignment_changed = pyqtSignal()             # 通道分配变化

    NUM_COLUMNS = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        # 144个通道状态字典
        self._channel_states: dict[int, ChannelState] = {
            i: ChannelState(i) for i in range(1, MAX_CHANNELS + 1)
        }
        # 每列当前显示的通道号（1~144）
        self.column_channels: list[int] = list(range(1, self.NUM_COLUMNS + 1))
        self._midi_engine = None

    def set_midi_engine(self, engine):
        """注入MIDI引擎"""
        self._midi_engine = engine

    def get_channel_state(self, ch_num: int) -> ChannelState:
        """获取指定通道的状态"""
        ch_num = max(1, min(MAX_CHANNELS, ch_num))
        return self._channel_states[ch_num]

    def get_column_channel(self, col_idx: int) -> int:
        """获取指定列当前显示的通道号"""
        return self.column_channels[col_idx]

    def set_column_channel(self, col_idx: int, ch_num: int):
        """设置指定列显示的通道号（翻页后调用）"""
        ch_num = max(1, min(MAX_CHANNELS, ch_num))
        self.column_channels[col_idx] = ch_num
        self.channel_assignment_changed.emit()

    # ----------------------------------------------------------------
    # 推子控制
    # ----------------------------------------------------------------
    def on_fader_moved(self, col_idx: int, midi_value: int):
        """推子移动处理"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        ch.fader = midi_value
        # MIDI CC7, 通道号 = (ch_num-1)%16+1 (映射到1~16)
        midi_ch = (ch_num - 1) % 16 + 1
        db_str = midi_to_db(midi_value)
        msg = (f"CC  列{col_idx + 1}→CH{ch_num} | "
               f"CC#{CC_FADER_VOLUME:02d} = {midi_value:3d} ({db_str} dB)")
        self._send_cc(midi_ch, CC_FADER_VOLUME, midi_value, msg)
        self.fader_changed.emit(col_idx, midi_value)

    # ----------------------------------------------------------------
    # 编码器控制
    # ----------------------------------------------------------------
    def on_encoder_rotated(self, col_idx: int, delta: int):
        """编码器旋转处理（delta已包含加速度系数）"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        midi_ch = (ch_num - 1) % 16 + 1

        if ch.enc_mode == ENC_MODE_COMP:
            # 压缩器阈值 -60~0 dB
            ch.comp_thr = max(-60.0, min(0.0, ch.comp_thr + delta))
            midi_val = comp_thr_to_midi(ch.comp_thr)
            msg = (f"CC  列{col_idx + 1}→CH{ch_num} | "
                   f"CC#{CC_COMP_THR:02d} = {midi_val:3d} "
                   f"(COMP THR {ch.comp_thr:+.1f}dB)")
            self._send_cc(midi_ch, CC_COMP_THR, midi_val, msg)

        elif ch.enc_mode == ENC_MODE_GATE:
            # 噪声门阈值 -80~0 dB
            ch.gate_thr = max(-80.0, min(0.0, ch.gate_thr + delta))
            midi_val = gate_thr_to_midi(ch.gate_thr)
            msg = (f"CC  列{col_idx + 1}→CH{ch_num} | "
                   f"CC#{CC_GATE_THR:02d} = {midi_val:3d} "
                   f"(GATE THR {ch.gate_thr:+.1f}dB)")
            self._send_cc(midi_ch, CC_GATE_THR, midi_val, msg)

        else:  # ENC_MODE_PAN
            # 声像 -63~63
            ch.pan = max(-63, min(63, ch.pan + delta))
            midi_val = pan_to_midi(ch.pan)
            pan_str = "C" if ch.pan == 0 else (
                f"L{abs(ch.pan)}" if ch.pan < 0 else f"R{ch.pan}")
            msg = (f"CC  列{col_idx + 1}→CH{ch_num} | "
                   f"CC#{CC_PAN:02d} = {midi_val:3d} (PAN {pan_str})")
            self._send_cc(midi_ch, CC_PAN, midi_val, msg)

        self.encoder_changed.emit(col_idx, midi_val)

    def on_encoder_clicked(self, col_idx: int):
        """编码器单击 - 循环切换3个模式"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        ch.enc_mode = (ch.enc_mode + 1) % 3
        mode_name = ENC_MODE_NAMES[ch.enc_mode]
        msg = f"ENC 列{col_idx + 1}→CH{ch_num} | 模式切换 → {mode_name}"
        self.midi_message_sent.emit(msg)
        self.encoder_mode_changed.emit(col_idx, ch.enc_mode)

    # ----------------------------------------------------------------
    # 按键控制
    # ----------------------------------------------------------------
    def on_mute_clicked(self, col_idx: int):
        """MUTE按键（Toggle，红色LED）"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        ch.mute = not ch.mute
        note = (ch_num - 1) % 128
        velocity = 127 if ch.mute else 0
        msg = (f"NOTE 列{col_idx + 1}→CH{ch_num} | "
               f"MUTE Note#{note} {'ON ' if ch.mute else 'OFF'} ({velocity})")
        self._send_note(1, note, velocity, msg)
        self.button_changed.emit(col_idx, "mute", ch.mute)

    def on_solo_clicked(self, col_idx: int):
        """SOLO按键（Toggle，蓝色LED）"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        ch.solo = not ch.solo
        note = (ch_num - 1) % 128
        velocity = 127 if ch.solo else 0
        msg = (f"NOTE 列{col_idx + 1}→CH{ch_num} | "
               f"SOLO Note#{note} {'ON ' if ch.solo else 'OFF'} ({velocity})")
        self._send_note(2, note, velocity, msg)
        self.button_changed.emit(col_idx, "solo", ch.solo)

    def on_dyn_clicked(self, col_idx: int):
        """DYN ON/OFF按键（Toggle，橙色LED）- 动态处理总开关"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        ch.dyn_on = not ch.dyn_on
        note = (ch_num - 1) % 128
        velocity = 127 if ch.dyn_on else 0
        msg = (f"NOTE 列{col_idx + 1}→CH{ch_num} | "
               f"DYN  Note#{note} {'ON ' if ch.dyn_on else 'OFF'} ({velocity})")
        self._send_note(4, note, velocity, msg)
        self.button_changed.emit(col_idx, "dyn", ch.dyn_on)

    def on_sel_clicked(self, col_idx: int):
        """SEL按键（白色LED，同时只能一列激活）"""
        ch_num = self.column_channels[col_idx]
        ch = self._channel_states[ch_num]
        was_active = ch.select

        # 取消所有列的SELECT状态
        for i in range(self.NUM_COLUMNS):
            other_ch_num = self.column_channels[i]
            other_ch = self._channel_states[other_ch_num]
            if other_ch.select:
                other_ch.select = False
                self.button_changed.emit(i, "sel", False)

        # 若之前未激活，则激活当前列
        if not was_active:
            ch.select = True
            note = (ch_num - 1) % 128
            msg = (f"NOTE 列{col_idx + 1}→CH{ch_num} | "
                   f"SEL  Note#{note} ON  (127)")
            self._send_note(3, note, 127, msg)
            self.button_changed.emit(col_idx, "sel", True)
        else:
            note = (ch_num - 1) % 128
            msg = (f"NOTE 列{col_idx + 1}→CH{ch_num} | "
                   f"SEL  Note#{note} OFF (0)")
            self._send_note(3, note, 0, msg)

    # ----------------------------------------------------------------
    # 内部MIDI发送辅助
    # ----------------------------------------------------------------
    def _send_cc(self, midi_channel: int, cc: int, value: int, log_msg: str):
        """发送MIDI CC消息并记录日志"""
        if self._midi_engine:
            self._midi_engine.send_cc(midi_channel, cc, value)
        self.midi_message_sent.emit(log_msg)

    def _send_note(self, midi_channel: int, note: int,
                   velocity: int, log_msg: str):
        """发送MIDI Note消息并记录日志"""
        if self._midi_engine:
            if velocity > 0:
                self._midi_engine.send_note_on(midi_channel, note, velocity)
            else:
                self._midi_engine.send_note_off(midi_channel, note)
        self.midi_message_sent.emit(log_msg)

    # ----------------------------------------------------------------
    # 向后兼容属性
    # ----------------------------------------------------------------
    @property
    def channels(self) -> list[ChannelState]:
        """按列索引返回当前通道状态列表（兼容旧接口）"""
        return [self._channel_states[self.column_channels[i]]
                for i in range(self.NUM_COLUMNS)]

