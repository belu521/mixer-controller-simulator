# mixer_simulator/ui/style.py
# 颜色方案常量 - Yamaha DM Series Controller Simulator v2.0

# 背景色
BG_DARK = "#1a1a1a"
BG_PANEL = "#2d2d2d"
BG_CHANNEL = "#252525"

# 推子轨道
FADER_TRACK = "#404040"
FADER_THUMB = "#b0b0b0"

# 编码器
ENCODER_BG = "#333333"

# LED 颜色
LED_OFF = "#333333"
LED_WHITE = "#ffffff"
LED_CYAN = "#00ffff"
LED_YELLOW = "#ffff00"
LED_GREEN = "#00ff44"
LED_RED = "#ff2244"
LED_BLUE = "#0088ff"
LED_ORANGE = "#ff8800"

# LCD 颜色
LCD_BG = "#001a00"
LCD_TEXT = "#00ff44"
LCD_HIGHLIGHT = "#ffff00"
LCD_MUTE_BG = "#3a0000"

# 文字颜色
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#888888"
TEXT_LABEL = "#aaaaaa"

# 边框
BORDER_COLOR = "#404040"

# 全局样式表
GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
}}
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: "Consolas", "Courier New", monospace;
}}
QLabel {{
    color: {TEXT_LABEL};
    font-size: 11px;
}}
QPushButton {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}}
QPushButton:hover {{
    background-color: #383838;
    border-color: #666666;
}}
QPushButton:pressed {{
    background-color: #404040;
}}
QComboBox {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    min-width: 160px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    selection-background-color: #404040;
    border: 1px solid {BORDER_COLOR};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #555555;
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}
QTextEdit {{
    background-color: #111111;
    color: #00cc44;
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10px;
    padding: 4px;
}}
QToolTip {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    font-size: 11px;
    padding: 4px;
}}
QStatusBar {{
    background-color: {BG_PANEL};
    color: {TEXT_SECONDARY};
    font-size: 10px;
    border-top: 1px solid {BORDER_COLOR};
}}
"""
