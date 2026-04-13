# ui/style.py
# 全局样式表 - 深色专业混音台主题

# ============================================================
# 颜色规范
# ============================================================

# 背景色
BG_DARK = "#1a1a1a"        # 主背景
BG_PANEL = "#2d2d2d"       # 面板背景
BG_CHANNEL = "#252525"     # 通道背景

# 控件颜色
FADER_TRACK = "#404040"    # 推子轨道
FADER_THUMB = "#b0b0b0"    # 推子手柄
ENCODER_BG = "#333333"     # 编码器背景
ENCODER_DOT = "#00ff88"    # 编码器指示点

# LED颜色
LED_OFF = "#1a1a1a"
LED_WHITE = "#ffffff"      # 编码器默认激活
LED_CYAN = "#00ffff"       # EQ模式
LED_YELLOW = "#ffff00"     # PAN模式
LED_GREEN = "#00ff00"      # 按键激活
LED_RED = "#ff0000"        # MUTE静音
LED_BLUE = "#0088ff"       # SOLO独奏
LED_ORANGE = "#ff8800"     # REC录音

# LCD颜色
LCD_BG = "#001100"         # LCD背景（深绿）
LCD_TEXT = "#00ff44"       # LCD文字（绿色）

# 文字颜色
TEXT_PRIMARY = "#e0e0e0"   # 主要文字
TEXT_SECONDARY = "#888888" # 次要文字
TEXT_LABEL = "#aaaaaa"     # 标签文字

# 分隔线颜色
BORDER_COLOR = "#404040"


# ============================================================
# 全局样式表
# ============================================================

GLOBAL_STYLESHEET = f"""
/* 主窗口 */
QMainWindow {{
    background-color: {BG_DARK};
}}

/* 全局控件 */
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: "Consolas", "Courier New", monospace;
}}

/* 标签 */
QLabel {{
    color: {TEXT_LABEL};
    font-size: 11px;
}}

/* 按钮 */
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

/* 下拉框 */
QComboBox {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    min-width: 160px;
}}

QComboBox:hover {{
    border-color: #666666;
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

/* 滚动条 */
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

/* 文本区域（MIDI日志） */
QTextEdit {{
    background-color: #111111;
    color: #00cc44;
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10px;
    padding: 4px;
}}

/* 工具提示 */
QToolTip {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    font-size: 11px;
    padding: 4px;
}}

/* 状态栏 */
QStatusBar {{
    background-color: {BG_PANEL};
    color: {TEXT_SECONDARY};
    font-size: 10px;
    border-top: 1px solid {BORDER_COLOR};
}}

/* 分割线 */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    color: {BORDER_COLOR};
}}
"""

# 通道条样式
CHANNEL_STRIP_STYLE = f"""
QFrame#channelStrip {{
    background-color: {BG_CHANNEL};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
}}
"""
