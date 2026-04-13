# core/controller.py
# 核心控制器逻辑 - 状态管理

from PyQt6.QtCore import QObject, pyqtSignal

# 编码器模式定义
ENCODER_MODE_DEFAULT = "VOL"   # 默认音量模式
ENCODER_MODE_EQ = "EQ"         # EQ均衡模式
ENCODER_MODE_PAN = "PAN"       # 声像模式

# 编码器模式循环顺序
ENCODER_MODES = [ENCODER_MODE_DEFAULT, ENCODER_MODE_EQ, ENCODER_MODE_PAN]

# MIDI CC映射
# 推子: CH1=CC1, CH2=CC2 ... CH5=CC5
FADER_CC_BASE = 1
# 编码器: CH1=CC11, CH2=CC12 ... CH5=CC15
ENCODER_CC_BASE = 11

# 按键MIDI Note映射（每列4个按键）
# 上方按键1(MUTE): Note 0~4
# 上方按键2(SOLO): Note 5~9
# 下方按键1(REC):  Note 10~14
# 下方按键2(SEL):  Note 15~19
BTN_MUTE_NOTE_BASE = 0
BTN_SOLO_NOTE_BASE = 5
BTN_REC_NOTE_BASE = 10
BTN_SEL_NOTE_BASE = 15

# MIDI值到dB换算常量
MIDI_0DB_VALUE = 100   # MIDI值100 = 0 dB
MIDI_MAX_VALUE = 127   # MIDI值127 = +6 dB


def midi_to_db(midi_value: int) -> str:
    """将MIDI值(0-127)转换为dB字符串显示"""
    if midi_value == 0:
        return "-inf"
    elif midi_value <= MIDI_0DB_VALUE:
        # 0 ~ -inf 线性插值: MIDI值1~100对应-60~0dB
        db = (midi_value / MIDI_0DB_VALUE) * 60.0 - 60.0
        return f"{db:.1f}"
    else:
        # 100 ~ 127 对应 0 ~ +6 dB
        db = ((midi_value - MIDI_0DB_VALUE) / (MIDI_MAX_VALUE - MIDI_0DB_VALUE)) * 6.0
        return f"+{db:.1f}"


class ChannelState:
    """单通道状态"""

    def __init__(self, channel_id: int):
        self.channel_id = channel_id          # 通道编号 (0-4)
        self.channel_name = f"CH{channel_id + 1}"  # 通道名称

        # 推子状态
        self.fader_value = 100                # 推子MIDI值 (0-127)，默认100=0dB

        # 编码器状态
        self.encoder_value = 64               # 编码器MIDI值 (0-127)，默认64
        self.encoder_mode_index = 0           # 编码器模式索引

        # 按键状态 (Toggle开关)
        self.mute_active = False              # 上方按键1: MUTE静音
        self.solo_active = False              # 上方按键2: SOLO独奏
        self.rec_active = False               # 下方按键1: REC录音
        self.sel_active = False               # 下方按键2: SEL选择/激活

    @property
    def encoder_mode(self) -> str:
        """当前编码器模式名称"""
        return ENCODER_MODES[self.encoder_mode_index]

    @property
    def fader_db(self) -> str:
        """推子dB值字符串"""
        return midi_to_db(self.fader_value)

    def next_encoder_mode(self) -> str:
        """切换到下一个编码器模式，返回新模式名称"""
        self.encoder_mode_index = (self.encoder_mode_index + 1) % len(ENCODER_MODES)
        return self.encoder_mode

    def toggle_mute(self) -> bool:
        """切换MUTE状态"""
        self.mute_active = not self.mute_active
        return self.mute_active

    def toggle_solo(self) -> bool:
        """切换SOLO状态"""
        self.solo_active = not self.solo_active
        return self.solo_active

    def toggle_rec(self) -> bool:
        """切换REC状态"""
        self.rec_active = not self.rec_active
        return self.rec_active

    def toggle_sel(self) -> bool:
        """切换SEL状态"""
        self.sel_active = not self.sel_active
        return self.sel_active


class MixerController(QObject):
    """混音控制器核心逻辑 - 管理5个通道状态"""

    # 信号定义
    fader_changed = pyqtSignal(int, int)        # (channel_id, midi_value) 推子变化
    encoder_changed = pyqtSignal(int, int)      # (channel_id, midi_value) 编码器变化
    encoder_mode_changed = pyqtSignal(int, str) # (channel_id, mode) 编码器模式变化
    button_changed = pyqtSignal(int, str, bool) # (channel_id, btn_type, state) 按键变化
    midi_message_sent = pyqtSignal(str)         # MIDI消息日志

    NUM_CHANNELS = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化5个通道状态
        self.channels = [ChannelState(i) for i in range(self.NUM_CHANNELS)]
        self._midi_engine = None  # MIDI引擎，后续注入

    def set_midi_engine(self, engine):
        """注入MIDI引擎"""
        self._midi_engine = engine

    # ----------------------------------------------------------------
    # 推子控制
    # ----------------------------------------------------------------
    def on_fader_moved(self, channel_id: int, midi_value: int):
        """推子移动处理"""
        ch = self.channels[channel_id]
        ch.fader_value = midi_value
        cc_number = FADER_CC_BASE + channel_id
        msg = f"CC  CH{channel_id + 1} | CC#{cc_number:02d} = {midi_value:3d} ({ch.fader_db} dB)"
        self._send_cc(1, cc_number, midi_value, msg)
        self.fader_changed.emit(channel_id, midi_value)

    # ----------------------------------------------------------------
    # 编码器控制
    # ----------------------------------------------------------------
    def on_encoder_rotated(self, channel_id: int, delta: int):
        """编码器旋转处理 delta=+1右转/-1左转"""
        ch = self.channels[channel_id]
        new_value = max(0, min(127, ch.encoder_value + delta))
        ch.encoder_value = new_value
        cc_number = ENCODER_CC_BASE + channel_id
        msg = f"CC  CH{channel_id + 1} | CC#{cc_number:02d} = {new_value:3d} (ENC)"
        self._send_cc(1, cc_number, new_value, msg)
        self.encoder_changed.emit(channel_id, new_value)

    def on_encoder_clicked(self, channel_id: int):
        """编码器按键点击 - 切换功能模式"""
        ch = self.channels[channel_id]
        new_mode = ch.next_encoder_mode()
        msg = f"ENC CH{channel_id + 1} | 模式切换 → {new_mode}"
        self.midi_message_sent.emit(msg)
        self.encoder_mode_changed.emit(channel_id, new_mode)

    # ----------------------------------------------------------------
    # 按键控制
    # ----------------------------------------------------------------
    def on_mute_clicked(self, channel_id: int):
        """MUTE按键点击"""
        ch = self.channels[channel_id]
        state = ch.toggle_mute()
        note = BTN_MUTE_NOTE_BASE + channel_id
        velocity = 127 if state else 0
        msg = f"NOTE CH{channel_id + 1} | MUTE Note#{note} {'ON ' if state else 'OFF'} ({velocity})"
        self._send_note(1, note, velocity, msg)
        self.button_changed.emit(channel_id, "mute", state)

    def on_solo_clicked(self, channel_id: int):
        """SOLO按键点击"""
        ch = self.channels[channel_id]
        state = ch.toggle_solo()
        note = BTN_SOLO_NOTE_BASE + channel_id
        velocity = 127 if state else 0
        msg = f"NOTE CH{channel_id + 1} | SOLO Note#{note} {'ON ' if state else 'OFF'} ({velocity})"
        self._send_note(1, note, velocity, msg)
        self.button_changed.emit(channel_id, "solo", state)

    def on_rec_clicked(self, channel_id: int):
        """REC按键点击"""
        ch = self.channels[channel_id]
        state = ch.toggle_rec()
        note = BTN_REC_NOTE_BASE + channel_id
        velocity = 127 if state else 0
        msg = f"NOTE CH{channel_id + 1} | REC  Note#{note} {'ON ' if state else 'OFF'} ({velocity})"
        self._send_note(1, note, velocity, msg)
        self.button_changed.emit(channel_id, "rec", state)

    def on_sel_clicked(self, channel_id: int):
        """SEL按键点击"""
        ch = self.channels[channel_id]
        state = ch.toggle_sel()
        note = BTN_SEL_NOTE_BASE + channel_id
        velocity = 127 if state else 0
        msg = f"NOTE CH{channel_id + 1} | SEL  Note#{note} {'ON ' if state else 'OFF'} ({velocity})"
        self._send_note(1, note, velocity, msg)
        self.button_changed.emit(channel_id, "sel", state)

    # ----------------------------------------------------------------
    # 内部MIDI发送辅助
    # ----------------------------------------------------------------
    def _send_cc(self, midi_channel: int, cc: int, value: int, log_msg: str):
        """发送MIDI CC消息"""
        if self._midi_engine:
            self._midi_engine.send_cc(midi_channel, cc, value)
        self.midi_message_sent.emit(log_msg)

    def _send_note(self, midi_channel: int, note: int, velocity: int, log_msg: str):
        """发送MIDI Note消息"""
        if self._midi_engine:
            if velocity > 0:
                self._midi_engine.send_note_on(midi_channel, note, velocity)
            else:
                self._midi_engine.send_note_off(midi_channel, note)
        self.midi_message_sent.emit(log_msg)
