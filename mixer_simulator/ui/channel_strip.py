# ui/channel_strip.py
# 单通道条控件 - 整合LCD + 编码器 + 按键 + 推子

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .style import BG_CHANNEL, BORDER_COLOR, TEXT_LABEL, TEXT_PRIMARY
from .lcd_widget import LcdWidget
from .encoder_widget import EncoderWidget
from .button_widget import ButtonWidget, BTN_TYPE_MUTE, BTN_TYPE_SOLO, BTN_TYPE_REC, BTN_TYPE_SEL
from .fader_widget import FaderWidget


class ChannelStrip(QFrame):
    """单通道条控件
    
    严格按照PCB布局从上到下：
      1. LCD显示屏
      2. 编码器（旋钮+LED）
      3. 上方按键区（MUTE + SOLO，各自带LED）
      4. 推子（垂直滑块）
      5. 下方按键区（REC + SEL，各自带LED）
    """

    # 信号定义（透传给主控制器）
    fader_moved = pyqtSignal(int, int)         # (channel_id, value)
    encoder_rotated = pyqtSignal(int, int)     # (channel_id, delta)
    encoder_clicked = pyqtSignal(int)          # (channel_id)
    mute_clicked = pyqtSignal(int)             # (channel_id)
    solo_clicked = pyqtSignal(int)             # (channel_id)
    rec_clicked = pyqtSignal(int)              # (channel_id)
    sel_clicked = pyqtSignal(int)              # (channel_id)

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """初始化UI布局"""
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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ---- 通道标题 ----
        ch_label = QLabel(f"CH {self.channel_id + 1}")
        ch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ch_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            padding: 2px;
        """)
        main_layout.addWidget(ch_label)

        # ---- 分割线 ----
        main_layout.addWidget(self._make_separator())

        # ---- 1. LCD显示屏 ----
        self.lcd = LcdWidget(self.channel_id)
        main_layout.addWidget(self.lcd, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ---- 2. 编码器区域 ----
        self.encoder = EncoderWidget(self.channel_id)
        main_layout.addWidget(self.encoder, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ---- 分割线 ----
        main_layout.addWidget(self._make_separator())

        # ---- 3. 上方按键区（MUTE + SOLO） ----
        upper_btn_label = QLabel("上方按键")
        upper_btn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_btn_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        main_layout.addWidget(upper_btn_label)

        self.btn_mute = ButtonWidget(BTN_TYPE_MUTE)
        self.btn_mute.setToolTip(f"CH{self.channel_id + 1} MUTE - 静音\n点击切换")
        main_layout.addWidget(self.btn_mute, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_solo = ButtonWidget(BTN_TYPE_SOLO)
        self.btn_solo.setToolTip(f"CH{self.channel_id + 1} SOLO - 独奏\n点击切换")
        main_layout.addWidget(self.btn_solo, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ---- 分割线 ----
        main_layout.addWidget(self._make_separator())

        # ---- 4. 推子区域 ----
        fader_label = QLabel("FADER")
        fader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fader_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        main_layout.addWidget(fader_label)

        self.fader = FaderWidget(self.channel_id)
        main_layout.addWidget(self.fader, stretch=1, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ---- 分割线 ----
        main_layout.addWidget(self._make_separator())

        # ---- 5. 下方按键区（REC + SEL） ----
        lower_btn_label = QLabel("下方按键")
        lower_btn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lower_btn_label.setStyleSheet(f"color: {TEXT_LABEL}; font-size: 9px; background: transparent;")
        main_layout.addWidget(lower_btn_label)

        self.btn_rec = ButtonWidget(BTN_TYPE_REC)
        self.btn_rec.setToolTip(f"CH{self.channel_id + 1} REC - 录音\n点击切换")
        main_layout.addWidget(self.btn_rec, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_sel = ButtonWidget(BTN_TYPE_SEL)
        self.btn_sel.setToolTip(f"CH{self.channel_id + 1} SEL - 选择/激活\n点击切换")
        main_layout.addWidget(self.btn_sel, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _connect_signals(self):
        """连接控件信号到通道信号"""
        ch = self.channel_id

        # 推子
        self.fader.value_changed.connect(lambda v: self.fader_moved.emit(ch, v))

        # 编码器
        self.encoder.rotated.connect(lambda d: self.encoder_rotated.emit(ch, d))
        self.encoder.clicked.connect(lambda: self.encoder_clicked.emit(ch))

        # 按键
        self.btn_mute.clicked.connect(lambda: self.mute_clicked.emit(ch))
        self.btn_solo.clicked.connect(lambda: self.solo_clicked.emit(ch))
        self.btn_rec.clicked.connect(lambda: self.rec_clicked.emit(ch))
        self.btn_sel.clicked.connect(lambda: self.sel_clicked.emit(ch))

    def _make_separator(self) -> QFrame:
        """创建水平分割线"""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {BORDER_COLOR}; border: none;")
        return sep

    # ----------------------------------------------------------------
    # 状态更新接口（由控制器调用）
    # ----------------------------------------------------------------

    def update_fader_db(self, db_str: str):
        """更新LCD的dB显示"""
        self.lcd.set_db_value(db_str)

    def update_encoder_mode(self, mode: str):
        """更新编码器模式（LED颜色 + LCD显示）"""
        self.encoder.set_mode(mode)
        self.lcd.set_mode(mode)

    def update_encoder_value(self, value: int):
        """更新编码器值显示"""
        self.encoder.set_value_display(value)

    def update_button_state(self, btn_type: str, active: bool):
        """更新按键状态"""
        btn_map = {
            "mute": self.btn_mute,
            "solo": self.btn_solo,
            "rec":  self.btn_rec,
            "sel":  self.btn_sel,
        }
        btn = btn_map.get(btn_type)
        if btn:
            btn.set_active(active)
