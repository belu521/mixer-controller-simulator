# mixer_simulator/ui/main_window.py
# 主窗口 - Yamaha DM Series Controller Simulator v2.0

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit,
    QFrame, QScrollArea, QSizePolicy, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from mixer_simulator.ui.channel_strip import ChannelStrip
from mixer_simulator.ui.style import (
    GLOBAL_STYLESHEET, BG_DARK, BG_PANEL, TEXT_PRIMARY,
    TEXT_SECONDARY, BORDER_COLOR, LED_GREEN, TEXT_LABEL
)
from mixer_simulator.core.controller import MixerController, ENCODER_MODES
from mixer_simulator.midi.midi_engine import MidiEngine


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yamaha DM Series Controller Simulator v2.0")
        self.setMinimumSize(900, 1000)

        # 应用全局样式
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # 初始化控制器和MIDI引擎
        self._controller = MixerController(self)
        self._midi_engine = MidiEngine()
        self._controller.midi_engine = self._midi_engine

        # MIDI日志列表
        self._midi_log: list[str] = []

        self._setup_ui()
        self._connect_signals()
        self._init_strips()

    # ------------------------------------------------------------------ #
    # 构建界面
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)

        # 顶部工具栏
        root_layout.addWidget(self._build_toolbar())

        # 分割线
        root_layout.addWidget(self._make_separator())

        # 推子条区域
        strips_scroll = QScrollArea(self)
        strips_scroll.setWidgetResizable(True)
        strips_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        strips_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        strips_scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {BG_DARK}; }}"
        )

        strips_container = QWidget()
        strips_layout = QHBoxLayout(strips_container)
        strips_layout.setContentsMargins(4, 4, 4, 4)
        strips_layout.setSpacing(6)

        self._strips: list[ChannelStrip] = []
        for i in range(5):
            strip = ChannelStrip(i, strips_container)
            strips_layout.addWidget(strip)
            self._strips.append(strip)

        strips_layout.addStretch(1)
        strips_scroll.setWidget(strips_container)
        strips_scroll.setMinimumHeight(700)
        root_layout.addWidget(strips_scroll, stretch=1)

        # 分割线
        root_layout.addWidget(self._make_separator())

        # MIDI日志区
        root_layout.addWidget(self._build_midi_log())

        # 状态栏
        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)
        self._update_status_bar()

    def _build_toolbar(self) -> QWidget:
        """构建顶部工具栏"""
        toolbar = QWidget(self)
        toolbar.setStyleSheet(f"background-color: {BG_PANEL}; border-radius: 4px;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # 标题
        title = QLabel("Yamaha DM Series Controller Simulator  v2.0", toolbar)
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(title)
        layout.addStretch(1)

        # MIDI端口选择
        port_label = QLabel("MIDI端口:", toolbar)
        port_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(port_label)

        self._port_combo = QComboBox(toolbar)
        self._refresh_ports()
        layout.addWidget(self._port_combo)

        # 刷新端口按钮
        refresh_btn = QPushButton("刷新", toolbar)
        refresh_btn.setFixedWidth(50)
        refresh_btn.clicked.connect(self._refresh_ports)
        layout.addWidget(refresh_btn)

        # 连接/断开按钮
        self._connect_btn = QPushButton("连接", toolbar)
        self._connect_btn.setFixedWidth(60)
        self._connect_btn.clicked.connect(self._toggle_midi_connection)
        layout.addWidget(self._connect_btn)

        # 连接状态指示
        self._conn_label = QLabel("●  未连接", toolbar)
        self._conn_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self._conn_label)

        return toolbar

    def _build_midi_log(self) -> QWidget:
        """构建MIDI日志区域"""
        frame = QWidget(self)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        lbl = QLabel("MIDI 消息日志", frame)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px;")
        header.addWidget(lbl)
        header.addStretch(1)
        clear_btn = QPushButton("清空", frame)
        clear_btn.setFixedSize(40, 20)
        clear_btn.clicked.connect(self._clear_midi_log)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self._midi_log_widget = QTextEdit(frame)
        self._midi_log_widget.setReadOnly(True)
        self._midi_log_widget.setFixedHeight(100)
        self._midi_log_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        layout.addWidget(self._midi_log_widget)

        return frame

    def _make_separator(self) -> QFrame:
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {BORDER_COLOR};")
        return line

    # ------------------------------------------------------------------ #
    # 连接信号
    # ------------------------------------------------------------------ #

    def _connect_signals(self):
        """将推子条信号连接到控制器"""
        for strip in self._strips:
            sid = strip.strip_id
            strip.fader_moved.connect(self._controller.on_fader_moved)
            strip.encoder_rotated.connect(self._on_encoder_rotated)
            strip.encoder_single_clicked.connect(self._controller.on_encoder_clicked)
            strip.encoder_double_clicked.connect(self._controller.on_encoder_double_clicked)
            strip.mute_clicked.connect(self._controller.on_mute_clicked)
            strip.solo_clicked.connect(self._controller.on_solo_clicked)
            strip.select_clicked.connect(self._controller.on_select_clicked)
            strip.dyn_clicked.connect(self._controller.on_dyn_clicked)

        # 控制器 → UI更新
        self._controller.fader_changed.connect(self._on_fader_changed)
        self._controller.encoder_changed.connect(self._on_encoder_changed)
        self._controller.encoder_mode_changed.connect(self._on_encoder_mode_changed)
        self._controller.button_changed.connect(self._on_button_changed)
        self._controller.channel_switched.connect(self._on_channel_switched)
        self._controller.page_turn_mode_changed.connect(self._on_page_turn_changed)
        self._controller.midi_message_sent.connect(self._on_midi_message)
        self._controller.channel_assignment_changed.connect(self._update_status_bar)

    # ------------------------------------------------------------------ #
    # 初始化推子条显示
    # ------------------------------------------------------------------ #

    def _init_strips(self):
        """用控制器状态初始化所有推子条"""
        for i, strip in enumerate(self._strips):
            s = self._controller.get_strip_state(i)
            ch = self._controller.get_channel_state(s.current_channel)
            strip.update_from_channel_state(ch)

    # ------------------------------------------------------------------ #
    # 槽函数：来自控制器的信号
    # ------------------------------------------------------------------ #

    def _on_encoder_rotated(self, strip_id: int, delta: float):
        """将编码器旋转的float delta传递给控制器"""
        self._controller.on_encoder_rotated(strip_id, delta)

    def _on_fader_changed(self, strip_id: int, value: int):
        """推子值变化时更新LCD"""
        from mixer_simulator.ui.fader_widget import midi_to_db
        self._strips[strip_id]._lcd.set_fader_db(midi_to_db(value))

    def _on_encoder_changed(self, strip_id: int, val_str: str):
        """编码器参数变化时更新LCD"""
        s = self._controller.get_strip_state(strip_id)
        ch = self._controller.get_channel_state(s.current_channel)
        mode_name = ENCODER_MODES[ch.encoder_mode_index]
        self._strips[strip_id].update_encoder_display(mode_name, val_str)

    def _on_encoder_mode_changed(self, strip_id: int, mode_name: str):
        """编码器模式切换时更新LCD和编码器颜色"""
        s = self._controller.get_strip_state(strip_id)
        ch = self._controller.get_channel_state(s.current_channel)
        val_str = self._strips[strip_id].get_encoder_value_str(ch)
        self._strips[strip_id].update_encoder_display(mode_name, val_str)

    def _on_button_changed(self, strip_id: int, btn_type: str, state: bool):
        """按钮状态变化时更新UI"""
        self._strips[strip_id].update_button_state(btn_type, state)

    def _on_channel_switched(self, strip_id: int, old_ch: int, new_ch: int):
        """通道切换 - 开始推子校准动画"""
        ch = self._controller.get_channel_state(new_ch)
        self._strips[strip_id].start_channel_calibration(
            ch.fader_value, new_ch, ch.channel_name
        )
        # 校准完成后恢复完整UI状态
        def on_complete():
            self._strips[strip_id].update_from_channel_state(ch)
        self._strips[strip_id]._fader.calibration_complete.connect(on_complete)

    def _on_page_turn_changed(self, strip_id: int, is_page_turn: bool, target_ch: int):
        """翻页模式变化"""
        self._strips[strip_id].set_page_turn_mode(is_page_turn, target_ch)

    def _on_midi_message(self, msg: str):
        """记录MIDI消息到日志"""
        self._midi_log.append(msg)
        if len(self._midi_log) > 100:
            self._midi_log = self._midi_log[-100:]
        # 只显示最近10条
        display = "\n".join(self._midi_log[-10:])
        self._midi_log_widget.setPlainText(display)
        # 滚动到底部
        sb = self._midi_log_widget.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------ #
    # MIDI端口管理
    # ------------------------------------------------------------------ #

    def _refresh_ports(self):
        """刷新MIDI端口列表"""
        self._port_combo.clear()
        ports = self._midi_engine.get_ports()
        if ports:
            self._port_combo.addItems(ports)
        else:
            self._port_combo.addItem("（无可用端口）")

    def _toggle_midi_connection(self):
        """连接/断开MIDI端口"""
        if self._midi_engine.is_connected:
            self._midi_engine.disconnect()
            self._connect_btn.setText("连接")
            self._conn_label.setText("●  未连接")
            self._conn_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        else:
            port = self._port_combo.currentText()
            if port and port != "（无可用端口）":
                ok = self._midi_engine.connect(port)
                if ok:
                    self._connect_btn.setText("断开")
                    self._conn_label.setText(f"●  {port}")
                    self._conn_label.setStyleSheet(
                        f"color: {LED_GREEN}; font-size: 11px;"
                    )

    def _clear_midi_log(self):
        """清空MIDI日志"""
        self._midi_log.clear()
        self._midi_log_widget.clear()

    # ------------------------------------------------------------------ #
    # 状态栏
    # ------------------------------------------------------------------ #

    def _update_status_bar(self):
        """更新状态栏的通道分配概览"""
        channels = self._controller.get_all_strip_channels()
        parts = [f"列{i+1}:CH{ch}" for i, ch in enumerate(channels)]
        self._status_bar.showMessage(" | ".join(parts))
