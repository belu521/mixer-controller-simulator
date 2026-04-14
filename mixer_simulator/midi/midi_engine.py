# midi/midi_engine.py
# MIDI引擎 - 使用mido发送CC/Note消息，支持MIDI端口选择
# 注意：仅依赖mido，不使用python-rtmidi，避免Windows编译问题

from PyQt6.QtCore import QObject, pyqtSignal

# 仅尝试导入mido
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


class MidiEngine(QObject):
    """MIDI引擎 - 管理MIDI端口和消息发送
    
    mido无backend时优雅降级为模拟模式，不崩溃
    """

    # 连接状态变化信号
    connection_changed = pyqtSignal(bool, str)  # (is_connected, port_name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = False
        self._port_name = ""
        self._midi_out = None  # mido输出端口对象

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
        if MIDO_AVAILABLE:
            try:
                port_names = mido.get_output_names()
                ports.extend(port_names)
            except Exception:
                # mido无backend时返回空端口列表，降级模拟模式
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

        # 使用mido连接真实端口
        if MIDO_AVAILABLE:
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
            # 无mido库，使用模拟模式（日志显示MIDI未连接）
            self._connected = True
            self._port_name = "[MIDI未连接 - 模拟模式]"
            self.connection_changed.emit(True, self._port_name)
            return True

    def disconnect(self):
        """断开MIDI连接"""
        if self._midi_out is not None:
            try:
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
        if not MIDO_AVAILABLE:
            return
        try:
            msg = mido.Message('control_change',
                               channel=(channel - 1) & 0x0F,
                               control=cc & 0x7F,
                               value=value & 0x7F)
            self._midi_out.send(msg)
        except Exception:
            pass

    def send_note_on(self, channel: int, note: int, velocity: int = 127):
        """发送MIDI Note On消息"""
        if not self._connected or self._midi_out is None:
            return
        if not MIDO_AVAILABLE:
            return
        try:
            msg = mido.Message('note_on',
                               channel=(channel - 1) & 0x0F,
                               note=note & 0x7F,
                               velocity=velocity & 0x7F)
            self._midi_out.send(msg)
        except Exception:
            pass

    def send_note_off(self, channel: int, note: int):
        """发送MIDI Note Off消息"""
        if not self._connected or self._midi_out is None:
            return
        if not MIDO_AVAILABLE:
            return
        try:
            msg = mido.Message('note_off',
                               channel=(channel - 1) & 0x0F,
                               note=note & 0x7F,
                               velocity=0)
            self._midi_out.send(msg)
        except Exception:
            pass
