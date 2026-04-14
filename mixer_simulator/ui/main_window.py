# ui/main_window.py
# 主窗口 - 整体布局管理
# 升级：主音量旋钮、通道分配状态栏、连接新信号

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit,
    QStatusBar, QSizePolicy, QFrame, QDial
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont, QIcon

from .style import (
    GLOBAL_STYLESHEET, BG_DARK, BG_PANEL, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_LABEL, BORDER_COLOR
)
from .channel_strip import ChannelStrip
from ..core.controller import MixerController, midi_to_db
from ..midi.midi_engine import MidiEngine


class MasterVolumeWidget(QWidget):
    """主音量旋钮控件（滚轮/拖动调节，显示dB值）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 100   # MIDI 0~127，100 = 0dB
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)

        # QDial 旋钮
        self.dial = QDial()
        self.dial.setRange(0, 127)
        self.dial.setValue(self._value)
        self.dial.setFixedSize(36, 36)
        self.dial.setNotchesVisible(True)
        self.dial.setStyleSheet(f"""
            QDial {{
                background-color: #333333;
                color: {TEXT_PRIMARY};
            }}
        """)
        self.dial.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.dial)

        self.label = QLabel(self._fmt_label(self._value))
        self.label.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        layout.addWidget(self.label)

    def _fmt_label(self, v: int) -> str:
        db = midi_to_db(v)
        return f"■ 主音量 ({db}dB)" if db != '-inf' else "■ 主音量 (-∞)"

    def _on_value_changed(self, v: int):
        self._value = v
        self.label.setText(self._fmt_label(v))


class MainWindow(QMainWindow):
    """混音控制器模拟器主窗口
    
    布局（从上到下）：
      标题栏
      5个通道条（横向排列，每列独立寻址CH1~144）
      MIDI控制栏（含主音量旋钮）
      MIDI消息日志
      状态栏（含通道分配总览）
    """

    NUM_CHANNELS = 5
    MAX_LOG_LINES = 50   # MIDI日志最多保留50条

    def __init__(self):
        super().__init__()
        self._controller  = MixerController(self)
        self._midi_engine = MidiEngine(self)
        self._controller.set_midi_engine(self._midi_engine)

        self._setup_window()
        self._setup_ui()
        self._connect_signals()

        self._refresh_midi_ports()
        self._update_status("就绪 - 未连接MIDI")
        self._update_channel_assignment()

    def _setup_window(self):
        self.setWindowTitle(
            "混音控制器模拟器 v2.0 | Mixer Controller Simulator (DM Series)")
        self.setMinimumSize(800, 900)
        self.resize(940, 1040)
        self.setStyleSheet(GLOBAL_STYLESHEET)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(8)

        root.addWidget(self._build_title_bar())

        # ---- 通道条区域（5列，每列独立寻址）----
        ch_widget = QWidget()
        ch_layout = QHBoxLayout(ch_widget)
        ch_layout.setContentsMargins(0, 0, 0, 0)
        ch_layout.setSpacing(6)

        self.channel_strips: list[ChannelStrip] = []
        for col_id in range(self.NUM_CHANNELS):
            strip = ChannelStrip(col_id, self)
            self.channel_strips.append(strip)
            ch_layout.addWidget(strip)

        root.addWidget(ch_widget, stretch=1)
        root.addWidget(self._build_midi_bar())
        root.addWidget(self._build_log_area())

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
        # 通道分配总览（永久右侧显示）
        self._ch_assign_label = QLabel()
        self._ch_assign_label.setStyleSheet(
            "color: #88aacc; font-size: 9px; background: transparent;")
        self._status_bar.addPermanentWidget(self._ch_assign_label)
        self.setStatusBar(self._status_bar)

    # ----------------------------------------------------------------
    # 构建子区域
    # ----------------------------------------------------------------
    def _build_title_bar(self) -> QWidget:
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

        info = QLabel("5CH | 25×WS2812B | 5×EC11 | RSA0N11M9A0J×5")
        info.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        layout.addWidget(info)
        return widget

    def _build_midi_bar(self) -> QWidget:
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

        # MIDI端口选择
        port_lbl = QLabel("MIDI 输出端口：")
        port_lbl.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(port_lbl)

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
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background-color: #333333;
                color: {TEXT_PRIMARY};
                selection-background-color: #4a4a4a;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setFixedWidth(70)
        self.refresh_btn.clicked.connect(self._refresh_midi_ports)
        layout.addWidget(self.refresh_btn)

        self.connect_btn = QPushButton("▶ 连接")
        self.connect_btn.setFixedWidth(80)
        self.connect_btn.clicked.connect(self._toggle_midi_connection)
        layout.addWidget(self.connect_btn)

        # MIDI连接状态指示灯
        self.midi_status_led = QLabel("●")
        self.midi_status_led.setStyleSheet(
            "color: #ff4444; font-size: 14px; background: transparent; border: none;")
        layout.addWidget(self.midi_status_led)

        self.midi_status_label = QLabel("未连接")
        self.midi_status_label.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
        layout.addWidget(self.midi_status_label)

        layout.addStretch()

        # 主音量旋钮
        self.master_volume = MasterVolumeWidget(self)
        layout.addWidget(self.master_volume)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {BORDER_COLOR}; border: none;")
        layout.addWidget(sep)

        # 全部归位
        reset_btn = QPushButton("⏮ 全部归位 (0dB)")
        reset_btn.setFixedWidth(130)
        reset_btn.setToolTip("将所有推子归位到0dB (MIDI=100)")
        reset_btn.clicked.connect(self._reset_all_faders)
        layout.addWidget(reset_btn)

        return widget

    def _build_log_area(self) -> QWidget:
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

        header = QHBoxLayout()
        log_title = QLabel("MIDI 消息日志（最近50条）")
        log_title.setStyleSheet(
            f"color: {TEXT_LABEL}; font-size: 10px; background: transparent; border: none;")
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
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        clear_btn.clicked.connect(self._clear_log)
        header.addWidget(clear_btn)
        layout.addLayout(header)

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

    # ----------------------------------------------------------------
    # 信号连接
    # ----------------------------------------------------------------
    def _connect_signals(self):
        ctrl = self._controller

        for strip in self.channel_strips:
            strip.fader_moved.connect(ctrl.on_fader_moved)
            strip.encoder_rotated.connect(ctrl.on_encoder_rotated)
            strip.encoder_clicked.connect(ctrl.on_encoder_clicked)
            strip.mute_clicked.connect(ctrl.on_mute_clicked)
            strip.solo_clicked.connect(ctrl.on_solo_clicked)
            strip.dyn_clicked.connect(ctrl.on_dyn_clicked)
            strip.sel_clicked.connect(ctrl.on_sel_clicked)
            # 翻页确认：通道切换请求
            strip.channel_change_requested.connect(
                self._on_channel_change_requested)

        # 控制器 → UI 更新
        ctrl.fader_changed.connect(self._on_fader_changed)
        ctrl.encoder_changed.connect(self._on_encoder_changed)
        ctrl.encoder_mode_changed.connect(self._on_encoder_mode_changed)
        ctrl.button_changed.connect(self._on_button_changed)
        ctrl.midi_message_sent.connect(self._append_log)
        ctrl.channel_assignment_changed.connect(self._update_channel_assignment)

        # MIDI引擎状态
        self._midi_engine.connection_changed.connect(
            self._on_midi_connection_changed)

    # ----------------------------------------------------------------
    # 控制器信号处理
    # ----------------------------------------------------------------
    def _on_fader_changed(self, col_idx: int, midi_value: int):
        """推子值变化（LCD电平由定时器自动更新，此处无需操作）"""
        pass

    def _on_encoder_changed(self, col_idx: int, midi_value: int):
        """编码器值变化 → 更新参数值标签 + LCD第3行"""
        ch_num  = self._controller.column_channels[col_idx]
        ch      = self._controller.get_channel_state(ch_num)
        strip   = self.channel_strips[col_idx]
        strip.encoder.set_value_display(str(midi_value))
        if not strip._calibrating and not strip._bank_mode:
            strip.lcd.set_encoder_state(ch.enc_mode, ch.comp_thr,
                                        ch.gate_thr, ch.pan)

    def _on_encoder_mode_changed(self, col_idx: int, mode_idx: int):
        """编码器模式切换 → 更新LED颜色 + LCD"""
        ch_num = self._controller.column_channels[col_idx]
        ch     = self._controller.get_channel_state(ch_num)
        strip  = self.channel_strips[col_idx]
        strip.encoder.set_mode(mode_idx)
        if not strip._calibrating and not strip._bank_mode:
            strip.lcd.set_encoder_state(ch.enc_mode, ch.comp_thr,
                                        ch.gate_thr, ch.pan)

    def _on_button_changed(self, col_idx: int, btn_type: str, state: bool):
        """按键状态变化 → 更新LED + LCD第4行"""
        strip  = self.channel_strips[col_idx]
        strip.update_button_state(btn_type, state)
        ch_num = self._controller.column_channels[col_idx]
        ch     = self._controller.get_channel_state(ch_num)
        if not strip._calibrating and not strip._bank_mode:
            strip.lcd.set_button_states(
                ch.mute, ch.solo, ch.select, ch.dyn_on)

    def _on_channel_change_requested(self, col_idx: int, new_ch_num: int):
        """翻页确认：切换列映射到新通道，启动校准动画"""
        self._controller.set_column_channel(col_idx, new_ch_num)
        ch   = self._controller.get_channel_state(new_ch_num)
        strip = self.channel_strips[col_idx]
        strip.switch_to_channel(
            ch_num      = new_ch_num,
            fader_value = ch.fader,
            ch_name     = ch.name,
            enc_mode    = ch.enc_mode,
            comp_thr    = ch.comp_thr,
            gate_thr    = ch.gate_thr,
            pan         = ch.pan,
            mute        = ch.mute,
            solo        = ch.solo,
            sel         = ch.select,
            dyn         = ch.dyn_on,
        )
        self._update_channel_assignment()

    # ----------------------------------------------------------------
    # MIDI日志
    # ----------------------------------------------------------------
    def _append_log(self, message: str):
        """追加MIDI消息日志（时间戳格式：[HH:MM:SS.mmm]）"""
        ts   = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        line = f"[{ts}] {message}"
        self.log_text.append(line)

        # 超出50行删除最旧一行
        doc = self.log_text.document()
        while doc.blockCount() > self.MAX_LOG_LINES:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum())

    def _clear_log(self):
        self.log_text.clear()

    # ----------------------------------------------------------------
    # 状态栏：通道分配总览
    # ----------------------------------------------------------------
    def _update_channel_assignment(self):
        """更新状态栏通道分配总览：列1:CH1 | 列2:CH8 | ..."""
        parts = [
            f"列{i + 1}:CH{self._controller.column_channels[i]}"
            for i in range(self.NUM_CHANNELS)
        ]
        self._ch_assign_label.setText(" | ".join(parts))

    # ----------------------------------------------------------------
    # MIDI端口管理
    # ----------------------------------------------------------------
    def _refresh_midi_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        self.port_combo.addItems(self._midi_engine.get_available_ports())
        idx = self.port_combo.findText(current)
        if idx >= 0:
            self.port_combo.setCurrentIndex(idx)

    def _toggle_midi_connection(self):
        if self._midi_engine.is_connected:
            self._midi_engine.disconnect()
        else:
            self._midi_engine.connect(self.port_combo.currentText())

    def _on_midi_connection_changed(self, connected: bool, port_name: str):
        if connected:
            self.connect_btn.setText("■ 断开")
            self.midi_status_led.setStyleSheet(
                "color: #44ff44; font-size: 14px; background: transparent; border: none;")
            self.midi_status_label.setText(f"已连接: {port_name}")
            self._update_status(f"MIDI已连接: {port_name}")
            self._append_log(f">>> MIDI连接成功: {port_name}")
        else:
            self.connect_btn.setText("▶ 连接")
            self.midi_status_led.setStyleSheet(
                "color: #ff4444; font-size: 14px; background: transparent; border: none;")
            self.midi_status_label.setText("未连接")
            self._update_status("MIDI已断开")

    def _update_status(self, message: str):
        self._status_bar.showMessage(message)

    # ----------------------------------------------------------------
    # 全局控制
    # ----------------------------------------------------------------
    def _reset_all_faders(self):
        """所有推子归位到0dB (MIDI=100)"""
        for i, strip in enumerate(self.channel_strips):
            ch_num = self._controller.column_channels[i]
            ch     = self._controller.get_channel_state(ch_num)
            ch.fader = 100
            strip.fader.slider._start_animation(100)

    def closeEvent(self, event):
        self._midi_engine.disconnect()
        super().closeEvent(event)

