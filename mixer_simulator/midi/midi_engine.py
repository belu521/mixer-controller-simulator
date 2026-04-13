# midi/midi_engine.py
# MIDI引擎 - 负责发送CC/Note消息，支持虚拟MIDI端口选择

from PyQt6.QtCore import QObject, pyqtSignal

# 尝试导入MIDI库
try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


class MidiEngine(QObject):
    """MIDI引擎 - 管理MIDI端口和消息发送"""

    # 连接状态变化信号
    connection_changed = pyqtSignal(bool, str)  # (is_connected, port_name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = False
        self._port_name = ""
        self._midi_out = None         # rtmidi 输出对象
        self._use_rtmidi = RTMIDI_AVAILABLE

    @property
    def is_connected(self) -> bool:
        """是否已连接MIDI端口"""
        return self._connected

    @property
    def port_name(self) -> str:
        """当前连接的端口名称"""
        return self._port_name

    def get_available_ports(self) -> list[str]:
        """获取可用的MIDI输出端口列表"""
        ports = ["[模拟模式 - 不发送MIDI]"]
        if RTMIDI_AVAILABLE:
            try:
                midi_out = rtmidi.MidiOut()
                port_names = midi_out.get_ports()
                ports.extend(port_names)
                del midi_out
            except Exception:
                pass
        elif MIDO_AVAILABLE:
            try:
                port_names = mido.get_output_names()
                ports.extend(port_names)
            except Exception:
                pass
        return ports

    def connect(self, port_name: str) -> bool:
        """连接到指定MIDI端口"""
        self.disconnect()

        # 模拟模式 - 不实际连接MIDI
        if port_name == "[模拟模式 - 不发送MIDI]" or not port_name:
            self._connected = True
            self._port_name = "[模拟模式]"
            self.connection_changed.emit(True, self._port_name)
            return True

        # 使用rtmidi连接真实端口
        if RTMIDI_AVAILABLE:
            try:
                self._midi_out = rtmidi.MidiOut()
                ports = self._midi_out.get_ports()
                if port_name in ports:
                    port_index = ports.index(port_name)
                    self._midi_out.open_port(port_index)
                else:
                    # 尝试创建虚拟端口（仅在macOS/Linux上支持）
                    self._midi_out.open_virtual_port(port_name)
                self._connected = True
                self._port_name = port_name
                self.connection_changed.emit(True, port_name)
                return True
            except Exception as e:
                self._midi_out = None
                self.connection_changed.emit(False, f"连接失败: {e}")
                return False
        elif MIDO_AVAILABLE:
            try:
                self._midi_out = mido.open_output(port_name)
                self._connected = True
                self._port_name = port_name
                self.connection_changed.emit(True, port_name)
                return True
            except Exception as e:
                self._midi_out = None
                self.connection_changed.emit(False, f"连接失败: {e}")
                return False
        else:
            # 无MIDI库，使用模拟模式
            self._connected = True
            self._port_name = "[无MIDI库 - 模拟模式]"
            self.connection_changed.emit(True, self._port_name)
            return True

    def disconnect(self):
        """断开MIDI连接"""
        if self._midi_out is not None:
            try:
                if RTMIDI_AVAILABLE and isinstance(self._midi_out, rtmidi.MidiOut):
                    self._midi_out.close_port()
                elif MIDO_AVAILABLE:
                    self._midi_out.close()
            except Exception:
                pass
            self._midi_out = None
        self._connected = False
        self._port_name = ""
        self.connection_changed.emit(False, "")

    def send_cc(self, channel: int, cc: int, value: int):
        """发送MIDI Control Change消息
        
        参数:
            channel: MIDI通道 (1-16)
            cc: CC编号 (0-127)
            value: CC值 (0-127)
        """
        if not self._connected or self._midi_out is None:
            return
        # MIDI CC状态字节: 0xB0 | (channel - 1)
        status = 0xB0 | ((channel - 1) & 0x0F)
        try:
            if RTMIDI_AVAILABLE and isinstance(self._midi_out, rtmidi.MidiOut):
                self._midi_out.send_message([status, cc & 0x7F, value & 0x7F])
            elif MIDO_AVAILABLE:
                msg = mido.Message('control_change', channel=channel - 1,
                                   control=cc, value=value)
                self._midi_out.send(msg)
        except Exception:
            pass

    def send_note_on(self, channel: int, note: int, velocity: int = 127):
        """发送MIDI Note On消息"""
        if not self._connected or self._midi_out is None:
            return
        status = 0x90 | ((channel - 1) & 0x0F)
        try:
            if RTMIDI_AVAILABLE and isinstance(self._midi_out, rtmidi.MidiOut):
                self._midi_out.send_message([status, note & 0x7F, velocity & 0x7F])
            elif MIDO_AVAILABLE:
                msg = mido.Message('note_on', channel=channel - 1,
                                   note=note, velocity=velocity)
                self._midi_out.send(msg)
        except Exception:
            pass

    def send_note_off(self, channel: int, note: int):
        """发送MIDI Note Off消息"""
        if not self._connected or self._midi_out is None:
            return
        status = 0x80 | ((channel - 1) & 0x0F)
        try:
            if RTMIDI_AVAILABLE and isinstance(self._midi_out, rtmidi.MidiOut):
                self._midi_out.send_message([status, note & 0x7F, 0])
            elif MIDO_AVAILABLE:
                msg = mido.Message('note_off', channel=channel - 1, note=note)
                self._midi_out.send(msg)
        except Exception:
            pass
