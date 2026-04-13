# ui/button_widget.py
# 按键+LED控件 - 模拟机械轴按键 + WS2812B LED

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .style import (
    BG_PANEL, TEXT_PRIMARY, TEXT_LABEL, BORDER_COLOR,
    LED_OFF, LED_GREEN, LED_RED, LED_BLUE, LED_ORANGE
)
from .encoder_widget import LedIndicator


# 按键类型定义
BTN_TYPE_MUTE = "mute"   # 静音 - LED红色
BTN_TYPE_SOLO = "solo"   # 独奏 - LED蓝色
BTN_TYPE_REC = "rec"     # 录音 - LED橙色
BTN_TYPE_SEL = "sel"     # 选择 - LED绿色

# 按键类型对应的颜色和标签
BTN_CONFIG = {
    BTN_TYPE_MUTE: {"label": "MUTE", "active_color": LED_RED,    "inactive_color": LED_OFF},
    BTN_TYPE_SOLO: {"label": "SOLO", "active_color": LED_BLUE,   "inactive_color": LED_OFF},
    BTN_TYPE_REC:  {"label": "REC",  "active_color": LED_ORANGE, "inactive_color": LED_OFF},
    BTN_TYPE_SEL:  {"label": "SEL",  "active_color": LED_GREEN,  "inactive_color": LED_OFF},
}


class ButtonWidget(QWidget):
    """机械轴按键 + WS2812B LED 控件
    
    布局（横向）：
      [LED] [按键]
    
    按键支持Toggle模式：按一次激活，再按一次关闭
    """

    clicked = pyqtSignal()  # 点击信号

    def __init__(self, btn_type: str, parent=None):
        super().__init__(parent)
        self.btn_type = btn_type
        self._active = False
        config = BTN_CONFIG.get(btn_type, BTN_CONFIG[BTN_TYPE_SEL])
        self._active_color = config["active_color"]
        self._label_text = config["label"]
        self._setup_ui()

    def _setup_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # WS2812B LED指示灯
        self.led = LedIndicator(LED_OFF)
        self.led.setToolTip(f"WS2812B LED\n{self._label_text}状态指示")
        layout.addWidget(self.led)

        # 机械轴按键
        self.button = QPushButton(self._label_text)
        self.button.setFixedSize(50, 26)
        self.button.setStyleSheet(self._get_button_style(False))
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self._on_button_clicked)
        layout.addWidget(self.button)

    def _get_button_style(self, active: bool) -> str:
        """获取按键样式"""
        if active:
            # 激活状态 - 更亮
            color_map = {
                BTN_TYPE_MUTE: "#cc2222",
                BTN_TYPE_SOLO: "#1155cc",
                BTN_TYPE_REC:  "#cc6600",
                BTN_TYPE_SEL:  "#119911",
            }
            bg_color = color_map.get(self.btn_type, "#444444")
            return f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: #ffffff;
                    border: 1px solid {bg_color};
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }}
                QPushButton:hover {{
                    background-color: {bg_color};
                    filter: brightness(1.2);
                }}
                QPushButton:pressed {{
                    border-style: inset;
                    border-width: 2px;
                }}
            """
        else:
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

    def _on_button_clicked(self):
        """按键点击处理 - Toggle模式"""
        self.clicked.emit()

    def set_active(self, active: bool):
        """设置激活状态"""
        self._active = active
        self.button.setStyleSheet(self._get_button_style(active))
        if active:
            self.led.set_color(self._active_color)
        else:
            self.led.set_color(LED_OFF)

    @property
    def is_active(self) -> bool:
        """当前是否激活"""
        return self._active
