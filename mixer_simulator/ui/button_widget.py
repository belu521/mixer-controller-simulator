# ui/button_widget.py
# 按键+LED控件 - 模拟机械轴按键（键帽无字）+ WS2812B LED
# 升级：REC → DYN ON/OFF（橙色LED），SEL → 白色LED

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from .style import (
    BG_PANEL, TEXT_PRIMARY, TEXT_LABEL, BORDER_COLOR,
    LED_OFF, LED_WHITE, LED_RED, LED_BLUE, LED_ORANGE
)
from .encoder_widget import LedIndicator


# ---- 按键类型定义 ----
BTN_TYPE_MUTE = "mute"   # 静音          红色LED  #ff0000
BTN_TYPE_SOLO = "solo"   # 独奏          蓝色LED  #0088ff
BTN_TYPE_DYN  = "dyn"    # DYN ON/OFF   橙色LED  #ff8800  (原REC替换)
BTN_TYPE_SEL  = "sel"    # 通道选择      白色LED  #ffffff

# 保留旧名用于向后兼容（已废弃，不应在新代码中使用）
BTN_TYPE_REC = BTN_TYPE_DYN

# ---- 按键类型配置 ----
BTN_CONFIG = {
    BTN_TYPE_MUTE: {
        "label": "MUTE",
        "active_color": LED_RED,
        "active_bg": "#cc2222",
    },
    BTN_TYPE_SOLO: {
        "label": "SOLO",
        "active_color": LED_BLUE,
        "active_bg": "#1155cc",
    },
    BTN_TYPE_DYN: {
        "label": "DYN",
        "active_color": LED_ORANGE,
        "active_bg": "#cc6600",
    },
    BTN_TYPE_SEL: {
        "label": "SEL",
        "active_color": LED_WHITE,
        "active_bg": "#888888",
    },
}


class ButtonWidget(QWidget):
    """机械轴按键 + WS2812B LED 控件
    
    布局（横向）：
      [LED] [按键]
    
    按键支持Toggle模式：点击发出 clicked 信号，
    由外部控制器切换激活状态，再调用 set_active() 刷新UI。
    
    按键功能说明：
      MUTE - 通道静音，红色LED
      SOLO - 独奏监听，蓝色LED
      DYN  - 动态处理总开关（替代原REC），橙色LED
      SEL  - 通道选择（同一时间只有一列激活），白色LED
    """

    clicked = pyqtSignal()   # 按键点击信号

    def __init__(self, btn_type: str, parent=None):
        super().__init__(parent)
        self.btn_type = btn_type
        self._active = False
        config = BTN_CONFIG.get(btn_type, BTN_CONFIG[BTN_TYPE_SEL])
        self._active_color = config["active_color"]
        self._active_bg    = config["active_bg"]
        self._label_text   = config["label"]
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # WS2812B LED
        self.led = LedIndicator(LED_OFF)
        self.led.setToolTip(
            f"WS2812B LED\n{self._label_text} 状态指示")
        layout.addWidget(self.led)

        # 机械轴按键（键帽无字，功能由LCD显示）
        self.button = QPushButton(self._label_text)
        self.button.setFixedSize(50, 26)
        self.button.setStyleSheet(self._btn_style(False))
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self._on_clicked)
        layout.addWidget(self.button)

    def _btn_style(self, active: bool) -> str:
        """生成按键样式表"""
        if active:
            bg = self._active_bg
            return f"""
                QPushButton {{
                    background-color: {bg};
                    color: #ffffff;
                    border: 1px solid {bg};
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }}
                QPushButton:hover {{
                    background-color: {bg};
                }}
                QPushButton:pressed {{
                    border-style: inset;
                    border-width: 2px;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {BG_PANEL};
                color: #888888;
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
                font-size: 10px;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: #383838;
                color: #aaaaaa;
                border-color: #666666;
            }}
            QPushButton:pressed {{
                background-color: #444444;
                border-style: inset;
            }}
        """

    def _on_clicked(self):
        self.clicked.emit()

    def set_active(self, active: bool):
        """设置激活状态（由控制器调用）"""
        self._active = active
        self.button.setStyleSheet(self._btn_style(active))
        self.led.set_color(self._active_color if active else LED_OFF)

    @property
    def is_active(self) -> bool:
        return self._active

