# mixer_simulator/ui/lcd_widget.py
# LCD显示部件 - 4行字符显示，带动态电平条和校准进度

import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from mixer_simulator.ui.style import (
    LCD_BG, LCD_TEXT, LCD_HIGHLIGHT, LCD_MUTE_BG
)

# 电平条字符
BAR_FULL = "▮"
BAR_EMPTY = "░"
BAR_CELLS = 8  # 电平条格子数


class LcdWidget(QWidget):
    """4行LCD显示部件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 100)

        # 当前显示状态
        self._ch_num = 1
        self._ch_name = "Channel"
        self._fader_db = "0dB"
        self._encoder_mode = "COMP"
        self._encoder_value = "-20.0dB"
        self._mute = False
        self._solo = False
        self._select = False
        self._dyn = True

        # 电平条动画状态
        self._level_cells = 0       # 当前电平格子数（0~8）
        self._peak_cell = 0         # 峰值格子
        self._peak_hold_ticks = 0   # 峰值保持计数（10个tick=1s）

        # 显示模式
        self._page_turn_mode = False
        self._page_turn_target = 1
        self._calibrating = False
        self._cal_progress = 0
        self._cal_target_ch = 1
        self._cal_ch_name = ""

        # 构建UI
        self._setup_ui()

        # 电平条动画定时器（100ms）
        self._level_timer = QTimer(self)
        self._level_timer.timeout.connect(self._animate_level)
        self._level_timer.start(100)

    def _setup_ui(self):
        """构建LCD显示界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(1)

        # 创建4行标签
        font = QFont("Consolas", 8)
        font.setStyleHint(QFont.StyleHint.Monospace)

        self._rows: list[QLabel] = []
        for _ in range(4):
            lbl = QLabel(self)
            lbl.setFont(font)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl.setFixedHeight(20)
            layout.addWidget(lbl)
            self._rows.append(lbl)

        self._apply_bg(self._mute)
        self._refresh()

    def _apply_bg(self, mute: bool):
        """根据MUTE状态更改背景色"""
        bg = LCD_MUTE_BG if mute else LCD_BG
        self.setStyleSheet(
            f"QWidget {{ background-color: {bg}; }}"
            f"QLabel {{ background-color: {bg}; color: {LCD_TEXT}; "
            f"font-family: 'Consolas','Courier New',monospace; font-size: 8pt; }}"
        )

    # ------------------------------------------------------------------ #
    # 公开设置接口
    # ------------------------------------------------------------------ #

    def set_channel(self, ch_num: int, ch_name: str):
        """设置通道号和名称"""
        self._ch_num = ch_num
        self._ch_name = ch_name
        self._refresh()

    def set_fader_db(self, db_str: str):
        """设置推子电平字符串"""
        self._fader_db = db_str
        self._refresh()

    def set_encoder_display(self, mode: str, value_str: str):
        """设置编码器模式和参数显示"""
        self._encoder_mode = mode
        self._encoder_value = value_str
        self._refresh()

    def set_button_states(self, mute: bool, solo: bool, select: bool, dyn: bool):
        """设置按钮状态（影响第4行和背景色）"""
        self._mute = mute
        self._solo = solo
        self._select = select
        self._dyn = dyn
        self._apply_bg(mute)
        self._refresh()

    def set_mute_active(self, active: bool):
        """单独设置MUTE状态"""
        self._mute = active
        self._apply_bg(active)
        self._refresh()

    def set_page_turn_mode(self, is_active: bool, target_ch: int):
        """进入/退出翻页模式显示"""
        self._page_turn_mode = is_active
        self._page_turn_target = target_ch
        self._calibrating = False
        self._refresh()

    def set_calibrating(self, is_active: bool, progress_pct: int,
                        target_ch: int, ch_name: str):
        """设置推子校准进度显示"""
        self._calibrating = is_active
        self._cal_progress = progress_pct
        self._cal_target_ch = target_ch
        self._cal_ch_name = ch_name
        self._page_turn_mode = False
        self._refresh()

    # ------------------------------------------------------------------ #
    # 内部刷新逻辑
    # ------------------------------------------------------------------ #

    def _refresh(self):
        """根据当前状态刷新4行文字"""
        if self._page_turn_mode:
            self._render_page_turn()
        elif self._calibrating:
            self._render_calibrating()
        else:
            self._render_normal()

    def _render_normal(self):
        """正常显示模式"""
        # 第1行：通道号 + 名称
        ch_str = f"CH{self._ch_num}"
        row1 = f"{ch_str:<5}{self._ch_name[:9]}"
        self._set_row(0, row1)

        # 第2行：电平条 + dB值
        filled = min(self._level_cells, BAR_CELLS)
        bar = BAR_FULL * filled + BAR_EMPTY * (BAR_CELLS - filled)
        db_part = self._fader_db[:6]
        row2 = f"{bar} {db_part}"
        self._set_row(1, row2)

        # 第3行：编码器模式 + 参数值
        mode_str = self._encoder_mode[:4]
        val_str = self._encoder_value[:8]
        row3 = f"{mode_str:<5}{val_str}"
        self._set_row(2, row3)

        # 第4行：按钮提示
        m_str = "[M] " if self._mute else " M  "
        sl_str = "[SL]" if self._solo else " SL "
        sel_str = "[SEL]" if self._select else " SEL "
        dyn_str = "[DYN]" if self._dyn else " DYN "
        row4 = f"{m_str}{sl_str}{sel_str}{dyn_str}"[:20]
        self._set_row(3, row4)

    def _render_page_turn(self):
        """翻页模式显示"""
        self._set_row(0, "◄ CH BANK ►")
        self._set_row(1, f"  < CH{self._page_turn_target} >")
        self._set_row(2, "旋转选通道")
        self._set_row(3, "按下确认")

    def _render_calibrating(self):
        """推子校准进度显示"""
        self._set_row(0, f">> CH{self._cal_target_ch}")
        self._set_row(1, self._cal_ch_name[:13])
        self._set_row(2, "推子校准中...")
        # 进度条：8格
        filled = int(self._cal_progress / 100 * 8)
        bar = "█" * filled + "░" * (8 - filled)
        self._set_row(3, f"{bar} {self._cal_progress}%")

    def _set_row(self, idx: int, text: str):
        """设置指定行文字"""
        self._rows[idx].setText(text)

    # ------------------------------------------------------------------ #
    # 电平条动画
    # ------------------------------------------------------------------ #

    def _animate_level(self):
        """每100ms更新一次电平条（随机动画 + 峰值保持）"""
        if self._page_turn_mode or self._calibrating:
            return

        # 随机目标电平（模拟输入信号）
        if self._mute:
            target = 0
        else:
            target = int(random.random() ** 2 * BAR_CELLS)

        # 平滑移动
        if target > self._level_cells:
            self._level_cells = min(BAR_CELLS, self._level_cells + 2)
        elif target < self._level_cells:
            self._level_cells = max(0, self._level_cells - 1)

        # 峰值保持
        if self._level_cells > self._peak_cell:
            self._peak_cell = self._level_cells
            self._peak_hold_ticks = 10  # 保持1秒（10×100ms）
        elif self._peak_hold_ticks > 0:
            self._peak_hold_ticks -= 1
        else:
            self._peak_cell = max(0, self._peak_cell - 1)

        self._refresh()
