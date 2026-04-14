# mixer_simulator/core/controller.py
# 混音台控制器核心逻辑 - 管理5个推子条和最多144个通道的状态

from PyQt6.QtCore import QObject, pyqtSignal

# 默认通道名称列表（用于演示）
_DEFAULT_CHANNEL_NAMES = [
    "Kick Drm", "Snare", "Hi-Hat", "OHL", "OHR",
    "Tom 1", "Tom 2", "Tom 3", "Bass Gtr", "Elec Gtr",
    "Acst Gtr", "Piano", "Keys", "Synth", "Pad",
    "Strings", "Brass 1", "Brass 2", "Sax", "Flute",
    "Vox Lead", "Vox Bkg1", "Vox Bkg2", "Vox Harm", "Choir",
    "FX Revrb", "FX Delay", "FX Chor", "Aux 1", "Aux 2",
    "Aux 3", "Aux 4",
]


def _default_name(ch_num: int) -> str:
    """根据通道号返回默认通道名称"""
    idx = (ch_num - 1) % len(_DEFAULT_CHANNEL_NAMES)
    return _DEFAULT_CHANNEL_NAMES[idx]


class ChannelState:
    """单个通道的完整状态（CH1~CH144）"""

    def __init__(self, ch_num: int):
        self.ch_num = ch_num                          # 通道号 1~144
        self.channel_name: str = _default_name(ch_num)
        self.fader_value: int = 100                   # 推子值 0~127
        self.mute_active: bool = False                # 静音
        self.solo_active: bool = False                # 独奏
        self.select_active: bool = False              # 选中
        self.dyn_active: bool = True                  # 动态处理开关
        self.comp_thr: float = -20.0                  # 压缩阈值 -60~0 dB
        self.gate_thr: float = -40.0                  # 门限阈值 -80~0 dB
        self.pan: int = 0                             # 声像 -63~63
        self.encoder_mode_index: int = 0              # 编码器模式 0=COMP,1=GATE,2=PAN


class StripState:
    """单个物理推子条的状态"""

    def __init__(self, strip_id: int, initial_channel: int):
        self.strip_id = strip_id                      # 物理条编号 0~4
        self.current_channel: int = initial_channel  # 当前映射的通道号
        self.page_turn_mode: bool = False             # 是否在翻页模式
        self.page_turn_target: int = initial_channel  # 翻页模式中选中的目标通道


# 编码器模式名称
ENCODER_MODES = ["COMP", "GATE", "PAN"]


class MixerController(QObject):
    """混音台控制器 - 管理5条推子条 + 最多144个通道状态"""

    # 推子移动信号（strip_id, midi_value 0~127）
    fader_changed = pyqtSignal(int, int)
    # 编码器参数变化信号（strip_id, 新参数值字符串）
    encoder_changed = pyqtSignal(int, str)
    # 编码器模式变化信号（strip_id, 模式名称）
    encoder_mode_changed = pyqtSignal(int, str)
    # 按钮状态变化信号（strip_id, 按钮类型, 状态）
    button_changed = pyqtSignal(int, str, bool)
    # 通道切换信号（strip_id, 旧通道, 新通道）
    channel_switched = pyqtSignal(int, int, int)
    # 翻页模式状态变化（strip_id, 是否进入翻页, 目标通道）
    page_turn_mode_changed = pyqtSignal(int, bool, int)
    # MIDI消息字符串（用于日志显示）
    midi_message_sent = pyqtSignal(str)
    # 通道分配概览变化
    channel_assignment_changed = pyqtSignal()

    # 默认起始通道（5条推子条）
    _DEFAULT_CHANNELS = [1, 8, 15, 23, 32]
    # 支持最大通道数
    MAX_CHANNELS = 144

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化所有通道状态
        self._channels: dict[int, ChannelState] = {
            i: ChannelState(i) for i in range(1, self.MAX_CHANNELS + 1)
        }

        # 初始化5条推子条状态
        self._strips: list[StripState] = [
            StripState(i, self._DEFAULT_CHANNELS[i]) for i in range(5)
        ]

        # MIDI 引擎（由外部注入）
        self.midi_engine = None

    # ------------------------------------------------------------------ #
    # 公开只读属性
    # ------------------------------------------------------------------ #

    def get_channel_state(self, ch_num: int) -> ChannelState:
        """获取指定通道状态，超出范围则返回临时对象"""
        if 1 <= ch_num <= self.MAX_CHANNELS:
            return self._channels[ch_num]
        return ChannelState(ch_num)

    def get_strip_state(self, strip_id: int) -> StripState:
        """获取推子条状态"""
        return self._strips[strip_id]

    def get_strip_channel(self, strip_id: int) -> int:
        """获取推子条当前映射的通道号"""
        return self._strips[strip_id].current_channel

    def get_all_strip_channels(self) -> list[int]:
        """返回5条推子条当前映射的通道号列表"""
        return [s.current_channel for s in self._strips]

    # ------------------------------------------------------------------ #
    # 推子操作
    # ------------------------------------------------------------------ #

    def on_fader_moved(self, strip_id: int, value: int):
        """处理推子移动（value: 0~127）"""
        strip = self._strips[strip_id]
        ch_state = self._channels[strip.current_channel]
        ch_state.fader_value = value
        # 发送 MIDI CC7（音量）
        self._send_cc(strip.current_channel, 7, value)
        self.fader_changed.emit(strip_id, value)

    # ------------------------------------------------------------------ #
    # 编码器操作
    # ------------------------------------------------------------------ #

    def on_encoder_rotated(self, strip_id: int, delta: int):
        """处理编码器旋转（delta 已含加速步长）"""
        strip = self._strips[strip_id]

        # 翻页模式：改变目标通道选择（delta转为整数步进）
        if strip.page_turn_mode:
            new_target = max(1, min(self.MAX_CHANNELS,
                                    strip.page_turn_target + int(round(delta))))
            strip.page_turn_target = new_target
            self.page_turn_mode_changed.emit(strip_id, True, new_target)
            return

        # 正常模式：调整对应参数
        ch_state = self._channels[strip.current_channel]
        mode_idx = ch_state.encoder_mode_index

        if mode_idx == 0:
            # COMP 模式：调整压缩阈值
            ch_state.comp_thr = max(-60.0, min(0.0, ch_state.comp_thr + delta * 0.5))
            val_str = f"{ch_state.comp_thr:.1f}dB"
            midi_val = int((ch_state.comp_thr + 60) / 60 * 127)
            self._send_cc(strip.current_channel, 18, max(0, min(127, midi_val)))
        elif mode_idx == 1:
            # GATE 模式：调整门限阈值
            ch_state.gate_thr = max(-80.0, min(0.0, ch_state.gate_thr + delta * 0.5))
            val_str = f"{ch_state.gate_thr:.1f}dB"
            midi_val = int((ch_state.gate_thr + 80) / 80 * 127)
            self._send_cc(strip.current_channel, 16, max(0, min(127, midi_val)))
        else:
            # PAN 模式：调整声像（整数步进）
            ch_state.pan = max(-63, min(63, ch_state.pan + int(delta)))
            if ch_state.pan < 0:
                val_str = f"L{abs(ch_state.pan)}"
            elif ch_state.pan > 0:
                val_str = f"R{ch_state.pan}"
            else:
                val_str = "C"
            midi_val = ch_state.pan + 64
            self._send_cc(strip.current_channel, 10, max(0, min(127, midi_val)))

        self.encoder_changed.emit(strip_id, val_str)

    def on_encoder_clicked(self, strip_id: int):
        """编码器单击：翻页模式下确认切换，否则循环切换编码器模式"""
        strip = self._strips[strip_id]

        if strip.page_turn_mode:
            # 确认通道切换
            self._switch_channel(strip_id, strip.page_turn_target)
            strip.page_turn_mode = False
            self.page_turn_mode_changed.emit(strip_id, False, strip.current_channel)
            return

        # 循环 COMP→GATE→PAN
        ch_state = self._channels[strip.current_channel]
        ch_state.encoder_mode_index = (ch_state.encoder_mode_index + 1) % 3
        mode_name = ENCODER_MODES[ch_state.encoder_mode_index]
        self.encoder_mode_changed.emit(strip_id, mode_name)

    def on_encoder_double_clicked(self, strip_id: int):
        """编码器双击：进入/退出翻页模式"""
        strip = self._strips[strip_id]
        if strip.page_turn_mode:
            # 退出翻页模式（取消）
            strip.page_turn_mode = False
            self.page_turn_mode_changed.emit(strip_id, False, strip.current_channel)
        else:
            # 进入翻页模式
            strip.page_turn_mode = True
            strip.page_turn_target = strip.current_channel
            self.page_turn_mode_changed.emit(strip_id, True, strip.page_turn_target)

    # ------------------------------------------------------------------ #
    # 按钮操作
    # ------------------------------------------------------------------ #

    def on_mute_clicked(self, strip_id: int):
        """MUTE 按钮点击（切换）"""
        ch_state = self._get_strip_channel_state(strip_id)
        ch_state.mute_active = not ch_state.mute_active
        note = (ch_state.ch_num - 1) % 128  # Note = 0 + (channel-1)
        if ch_state.mute_active:
            self._send_note_on(ch_state.ch_num, note)
        else:
            self._send_note_off(ch_state.ch_num, note)
        self.button_changed.emit(strip_id, "MUTE", ch_state.mute_active)

    def on_solo_clicked(self, strip_id: int):
        """SOLO 按钮点击（切换）"""
        ch_state = self._get_strip_channel_state(strip_id)
        ch_state.solo_active = not ch_state.solo_active
        note = (32 + ch_state.ch_num - 1) % 128  # Note = 32 + (channel-1)
        if ch_state.solo_active:
            self._send_note_on(ch_state.ch_num, note)
        else:
            self._send_note_off(ch_state.ch_num, note)
        self.button_changed.emit(strip_id, "SOLO", ch_state.solo_active)

    def on_select_clicked(self, strip_id: int):
        """SELECT 按钮点击（同一时刻只有一个条可以被选中）"""
        # 先取消所有其他条的 SELECT 状态
        target_ch = self._strips[strip_id].current_channel
        for i, strip in enumerate(self._strips):
            ch = self._channels[strip.current_channel]
            if i != strip_id and ch.select_active:
                ch.select_active = False
                self.button_changed.emit(i, "SELECT", False)

        ch_state = self._channels[target_ch]
        ch_state.select_active = not ch_state.select_active
        note = (64 + ch_state.ch_num - 1) % 128  # Note = 64 + (channel-1)
        if ch_state.select_active:
            self._send_note_on(ch_state.ch_num, note)
        else:
            self._send_note_off(ch_state.ch_num, note)
        self.button_changed.emit(strip_id, "SELECT", ch_state.select_active)

    def on_dyn_clicked(self, strip_id: int):
        """DYN 按钮点击（切换）"""
        ch_state = self._get_strip_channel_state(strip_id)
        ch_state.dyn_active = not ch_state.dyn_active
        note = (96 + ch_state.ch_num - 1) % 128  # Note = 96 + (channel-1)
        if ch_state.dyn_active:
            self._send_note_on(ch_state.ch_num, note)
        else:
            self._send_note_off(ch_state.ch_num, note)
        self.button_changed.emit(strip_id, "DYN", ch_state.dyn_active)

    # ------------------------------------------------------------------ #
    # 内部辅助方法
    # ------------------------------------------------------------------ #

    def _get_strip_channel_state(self, strip_id: int) -> ChannelState:
        """获取推子条当前映射通道的状态"""
        return self._channels[self._strips[strip_id].current_channel]

    def _switch_channel(self, strip_id: int, new_ch: int):
        """切换推子条到新通道，并触发推子校准动画"""
        strip = self._strips[strip_id]
        old_ch = strip.current_channel
        if old_ch == new_ch:
            return
        strip.current_channel = new_ch
        self.channel_switched.emit(strip_id, old_ch, new_ch)
        self.channel_assignment_changed.emit()

    def _midi_channel(self, ch_num: int) -> int:
        """计算 MIDI 通道号（1~16循环）"""
        return (ch_num - 1) % 16 + 1

    def _send_cc(self, ch_num: int, cc: int, value: int):
        """发送 MIDI CC 消息"""
        midi_ch = self._midi_channel(ch_num)
        msg = f"CC ch{midi_ch} cc{cc}={value} (源通道CH{ch_num})"
        self.midi_message_sent.emit(msg)
        if self.midi_engine:
            self.midi_engine.send_cc(midi_ch, cc, value)

    def _send_note_on(self, ch_num: int, note: int):
        """发送 MIDI Note On"""
        midi_ch = self._midi_channel(ch_num)
        msg = f"NoteOn ch{midi_ch} note{note} vel127 (源通道CH{ch_num})"
        self.midi_message_sent.emit(msg)
        if self.midi_engine:
            self.midi_engine.send_note_on(midi_ch, note, 127)

    def _send_note_off(self, ch_num: int, note: int):
        """发送 MIDI Note Off"""
        midi_ch = self._midi_channel(ch_num)
        msg = f"NoteOff ch{midi_ch} note{note} vel0 (源通道CH{ch_num})"
        self.midi_message_sent.emit(msg)
        if self.midi_engine:
            self.midi_engine.send_note_off(midi_ch, note, 0)
