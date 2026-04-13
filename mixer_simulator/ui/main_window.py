# ui/main_window.py
# 主窗口 - 整体布局管理

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit,
    QStatusBar, QSizePolicy, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon

from .style import (
    GLOBAL_STYLESHEET, BG_DARK, BG_PANEL, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_LABEL, BORDER_COLOR
)
from .channel_strip import ChannelStrip
from ..core.controller import MixerController
from ..midi.midi_engine import MidiEngine


class MainWindow(QMainWindow):
    """混音控制器模拟器主窗口
    
    布局（从上到下）：
      标题栏
      5个通道条（横向排列）
      MIDI控制栏
      MIDI消息日志
      状态栏
    """

    NUM_CHANNELS = 5
    MAX_LOG_LINES = 50  # 最多显示50条MIDI日志

    def __init__(self):
        super().__init__()
        # 初始化核心组件
        self._controller = MixerController(self)
        self._midi_engine = MidiEngine(self)
        self._controller.set_midi_engine(self._midi_engine)

        self._setup_window()
        self._setup_ui()
        self._connect_signals()

        # 初始化状态
        self._refresh_midi_ports()
        self._update_status("就绪 - 未连接MIDI")

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("混音控制器模拟器 v1.0 | Mixer Controller Simulator")
        self.setMinimumSize(800, 900)
        self.resize(920, 1020)
        self.setStyleSheet(GLOBAL_STYLESHEET)

    def _setup_ui(self):
        """搭建主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 8, 10, 8)
        root_layout.setSpacing(8)

        # ---- 标题区域 ----
        title_bar = self._build_title_bar()
        root_layout.addWidget(title_bar)

        # ---- 通道条区域（5列） ----
        channels_widget = QWidget()
        channels_layout = QHBoxLayout(channels_widget)
        channels_layout.setContentsMargins(0, 0, 0, 0)
        channels_layout.setSpacing(6)

        self.channel_strips: list[ChannelStrip] = []
        for ch_id in range(self.NUM_CHANNELS):
            strip = ChannelStrip(ch_id, self)
            self.channel_strips.append(strip)
            channels_layout.addWidget(strip)

        root_layout.addWidget(channels_widget, stretch=1)

        # ---- MIDI控制栏 ----
        midi_bar = self._build_midi_bar()
        root_layout.addWidget(midi_bar)

        # ---- MIDI消息日志 ----
        log_area = self._build_log_area()
        root_layout.addWidget(log_area)

        # ---- 状态栏 ----
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_PANEL};
                color: {TEXT_SECONDARY};
                font-size: 10px;
                border-top: 1px solid {BORDER_COLOR};
                padding: 2px 8px;
            }}
        """)
        self.setStatusBar(self._status_bar)

    def _build_title_bar(self) -> QWidget:
        """构建标题栏"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_PANEL};
                border-radius: 4px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)

        # 左侧：标题
        title = QLabel("🎛 混音控制器模拟器")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)

        layout.addStretch()

        # 右侧：PCB信息
        info = QLabel("5CH | 25×WS2812B | 5×EC11 | RSA0N11M9A0J×5")
        info.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        layout.addWidget(info)

        return widget

    def _build_midi_bar(self) -> QWidget:
        """构建MIDI控制栏"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        # MIDI端口标签
        port_label = QLabel("MIDI 输出端口：")
        port_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(port_label)

        # 端口选择下拉框
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        self.port_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #333333;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 11px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #333333;
                color: {TEXT_PRIMARY};
                selection-background-color: #4a4a4a;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        layout.addWidget(self.port_combo)

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setFixedWidth(70)
        self.refresh_btn.clicked.connect(self._refresh_midi_ports)
        layout.addWidget(self.refresh_btn)

        # 连接/断开按钮
        self.connect_btn = QPushButton("▶ 连接")
        self.connect_btn.setFixedWidth(80)
        self.connect_btn.clicked.connect(self._toggle_midi_connection)
        layout.addWidget(self.connect_btn)

        # 状态指示灯
        self.midi_status_led = QLabel("●")
        self.midi_status_led.setStyleSheet("color: #ff4444; font-size: 14px; background: transparent; border: none;")
        layout.addWidget(self.midi_status_led)

        self.midi_status_label = QLabel("未连接")
        self.midi_status_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        layout.addWidget(self.midi_status_label)

        layout.addStretch()

        # 全部归位按钮
        reset_btn = QPushButton("⏮ 全部归位 (0dB)")
        reset_btn.setFixedWidth(130)
        reset_btn.setToolTip("将所有推子归位到0dB位置 (MIDI=100)")
        reset_btn.clicked.connect(self._reset_all_faders)
        layout.addWidget(reset_btn)

        return widget

    def _build_log_area(self) -> QWidget:
        """构建MIDI消息日志区域"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
        """)
        widget.setFixedHeight(130)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 日志标题
        header = QHBoxLayout()
        log_title = QLabel("MIDI 消息日志（最近50条）")
        log_title.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        header.addWidget(log_title)
        header.addStretch()

        clear_btn = QPushButton("清空")
        clear_btn.setFixedSize(50, 20)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #333333;
                color: {TEXT_LABEL};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                font-size: 10px;
                padding: 1px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
            }}
        """)
        clear_btn.clicked.connect(self._clear_log)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0d1117;
                color: #00cc44;
                border: none;
                font-family: "Consolas", monospace;
                font-size: 9pt;
            }}
        """)
        layout.addWidget(self.log_text)

        return widget

    def _connect_signals(self):
        """连接信号"""
        ctrl = self._controller

        # 连接各通道条信号到控制器
        for strip in self.channel_strips:
            ch = strip.channel_id
            strip.fader_moved.connect(ctrl.on_fader_moved)
            strip.encoder_rotated.connect(ctrl.on_encoder_rotated)
            strip.encoder_clicked.connect(ctrl.on_encoder_clicked)
            strip.mute_clicked.connect(ctrl.on_mute_clicked)
            strip.solo_clicked.connect(ctrl.on_solo_clicked)
            strip.rec_clicked.connect(ctrl.on_rec_clicked)
            strip.sel_clicked.connect(ctrl.on_sel_clicked)

        # 控制器信号 → 更新UI
        ctrl.fader_changed.connect(self._on_fader_changed)
        ctrl.encoder_changed.connect(self._on_encoder_changed)
        ctrl.encoder_mode_changed.connect(self._on_encoder_mode_changed)
        ctrl.button_changed.connect(self._on_button_changed)
        ctrl.midi_message_sent.connect(self._append_log)

        # MIDI引擎信号
        self._midi_engine.connection_changed.connect(self._on_midi_connection_changed)

    def _on_fader_changed(self, channel_id: int, midi_value: int):
        """推子值变化 → 更新LCD dB显示"""
        ch_state = self._controller.channels[channel_id]
        self.channel_strips[channel_id].update_fader_db(ch_state.fader_db)

    def _on_encoder_changed(self, channel_id: int, midi_value: int):
        """编码器值变化 → 更新显示"""
        self.channel_strips[channel_id].update_encoder_value(midi_value)

    def _on_encoder_mode_changed(self, channel_id: int, mode: str):
        """编码器模式变化 → 更新通道条"""
        self.channel_strips[channel_id].update_encoder_mode(mode)

    def _on_button_changed(self, channel_id: int, btn_type: str, state: bool):
        """按键状态变化 → 更新通道条"""
        self.channel_strips[channel_id].update_button_state(btn_type, state)

    def _append_log(self, message: str):
        """追加MIDI消息日志"""
        from PyQt6.QtCore import QDateTime
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        line = f"[{timestamp}] {message}"
        self.log_text.append(line)

        # 限制行数
        doc = self.log_text.document()
        while doc.blockCount() > self.MAX_LOG_LINES:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()

    # ----------------------------------------------------------------
    # MIDI端口管理
    # ----------------------------------------------------------------

    def _refresh_midi_ports(self):
        """刷新MIDI端口列表"""
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = self._midi_engine.get_available_ports()
        self.port_combo.addItems(ports)
        # 恢复之前选中的端口
        idx = self.port_combo.findText(current)
        if idx >= 0:
            self.port_combo.setCurrentIndex(idx)

    def _toggle_midi_connection(self):
        """切换MIDI连接状态"""
        if self._midi_engine.is_connected:
            self._midi_engine.disconnect()
        else:
            port = self.port_combo.currentText()
            self._midi_engine.connect(port)

    def _on_midi_connection_changed(self, connected: bool, port_name: str):
        """MIDI连接状态变化"""
        if connected:
            self.connect_btn.setText("■ 断开")
            self.midi_status_led.setStyleSheet("color: #44ff44; font-size: 14px; background: transparent; border: none;")
            self.midi_status_label.setText(f"已连接: {port_name}")
            self._update_status(f"MIDI已连接: {port_name}")
            self._append_log(f">>> MIDI连接成功: {port_name}")
        else:
            self.connect_btn.setText("▶ 连接")
            self.midi_status_led.setStyleSheet("color: #ff4444; font-size: 14px; background: transparent; border: none;")
            self.midi_status_label.setText("未连接")
            self._update_status("MIDI已断开")

    def _update_status(self, message: str):
        """更新状态栏"""
        self._status_bar.showMessage(message)

    # ----------------------------------------------------------------
    # 全局控制
    # ----------------------------------------------------------------

    def _reset_all_faders(self):
        """将所有推子归位到0dB (MIDI=100)"""
        for strip in self.channel_strips:
            strip.fader.slider._start_animation(100)

    def closeEvent(self, event):
        """窗口关闭时断开MIDI"""
        self._midi_engine.disconnect()
        super().closeEvent(event)
