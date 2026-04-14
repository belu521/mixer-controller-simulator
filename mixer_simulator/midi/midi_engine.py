# mixer_simulator/midi/midi_engine.py
# MIDI引擎 - 仅使用mido，不依赖rtmidi

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    mido = None


def get_available_ports() -> list[str]:
    """获取可用的MIDI输出端口列表"""
    if not MIDO_AVAILABLE:
        return []
    try:
        return mido.get_output_names()
    except Exception:
        return []


class MidiEngine:
    """MIDI引擎 - 封装mido的输出操作"""

    def __init__(self):
        self._port = None        # 当前打开的MIDI端口
        self._port_name = None   # 当前端口名称
        self._available = MIDO_AVAILABLE

    @property
    def is_connected(self) -> bool:
        """是否已连接MIDI端口"""
        return self._port is not None

    @property
    def port_name(self) -> str:
        """当前连接的端口名称"""
        return self._port_name or "（未连接）"

    def get_ports(self) -> list[str]:
        """获取可用端口列表"""
        return get_available_ports()

    def connect(self, port_name: str) -> bool:
        """连接到指定MIDI端口，成功返回True"""
        if not self._available:
            return False
        try:
            self.disconnect()
            self._port = mido.open_output(port_name)
            self._port_name = port_name
            return True
        except Exception as e:
            print(f"[MidiEngine] 连接失败: {e}")
            self._port = None
            self._port_name = None
            return False

    def disconnect(self):
        """断开当前MIDI连接"""
        if self._port is not None:
            try:
                self._port.close()
            except Exception:
                pass
            self._port = None
            self._port_name = None

    def send_cc(self, midi_channel: int, cc: int, value: int):
        """发送 Control Change 消息（midi_channel: 1~16）"""
        if not self.is_connected:
            return
        try:
            msg = mido.Message(
                "control_change",
                channel=midi_channel - 1,  # mido使用0-based通道
                control=cc,
                value=max(0, min(127, value)),
            )
            self._port.send(msg)
        except Exception as e:
            print(f"[MidiEngine] send_cc 失败: {e}")

    def send_note_on(self, midi_channel: int, note: int, velocity: int = 127):
        """发送 Note On 消息"""
        if not self.is_connected:
            return
        try:
            msg = mido.Message(
                "note_on",
                channel=midi_channel - 1,
                note=max(0, min(127, note)),
                velocity=max(0, min(127, velocity)),
            )
            self._port.send(msg)
        except Exception as e:
            print(f"[MidiEngine] send_note_on 失败: {e}")

    def send_note_off(self, midi_channel: int, note: int, velocity: int = 0):
        """发送 Note Off 消息"""
        if not self.is_connected:
            return
        try:
            msg = mido.Message(
                "note_off",
                channel=midi_channel - 1,
                note=max(0, min(127, note)),
                velocity=max(0, min(127, velocity)),
            )
            self._port.send(msg)
        except Exception as e:
            print(f"[MidiEngine] send_note_off 失败: {e}")
