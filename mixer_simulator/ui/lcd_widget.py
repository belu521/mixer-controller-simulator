# ui/lcd_widget.py
# LCD/OLED模拟显示控件 - 模拟SSD1315 128×64 OLED显示屏

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .style import LCD_BG, LCD_TEXT


class LcdWidget(QFrame):
    """OLED液晶显示屏模拟控件
    
    显示3行内容：
      第1行：通道名（CH1~CH5）
      第2行：当前电平dB值
      第3行：当前编码器功能（VOL/EQ/PAN）
    """

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self._channel_name = f"CH{channel_id + 1}"
        self._db_value = "0.0"
        self._mode = "VOL"
        self._setup_ui()

    def _setup_ui(self):
        """初始化UI"""
        self.setObjectName("lcdWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedSize(120, 72)

        # LCD风格样式
        self.setStyleSheet(f"""
            QFrame#lcdWidget {{
                background-color: {LCD_BG};
                border: 2px solid #003300;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        # 等宽字体用于LCD风格
        lcd_font = QFont("Consolas", 11, QFont.Weight.Bold)
        lcd_font_large = QFont("Consolas", 13, QFont.Weight.Bold)

        # 第1行：通道名
        self.label_channel = QLabel(self._channel_name)
        self.label_channel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_channel.setFont(lcd_font_large)
        self.label_channel.setStyleSheet(f"color: {LCD_TEXT}; background: transparent;")

        # 第2行：dB值
        self.label_db = QLabel("  0.0 dB")
        self.label_db.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_db.setFont(lcd_font)
        self.label_db.setStyleSheet(f"color: {LCD_TEXT}; background: transparent;")

        # 第3行：编码器模式
        self.label_mode = QLabel("[VOL]")
        self.label_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mode.setFont(lcd_font)
        self.label_mode.setStyleSheet(f"color: {LCD_TEXT}; background: transparent;")

        layout.addWidget(self.label_channel)
        layout.addWidget(self.label_db)
        layout.addWidget(self.label_mode)

    def set_db_value(self, db_str: str):
        """更新dB显示值"""
        self._db_value = db_str
        if db_str == "-inf":
            self.label_db.setText("-inf dB")
        else:
            try:
                val = float(db_str)
                self.label_db.setText(f"{val:+.1f} dB")
            except ValueError:
                self.label_db.setText(f"{db_str} dB")

    def set_mode(self, mode: str):
        """更新编码器功能模式显示"""
        self._mode = mode
        self.label_mode.setText(f"[{mode}]")

    def set_channel_name(self, name: str):
        """更新通道名显示"""
        self._channel_name = name
        self.label_channel.setText(name)
