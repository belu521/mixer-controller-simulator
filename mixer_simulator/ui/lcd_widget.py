# ui/lcd_widget.py
# LCD/OLED模拟显示控件 - 模拟SSD1315 128×64 OLED显示屏
# 升级为4行显示 + 电平条动画 + 翻页模式 + 推子校准模式

import random
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from .style import LCD_BG, LCD_TEXT

# ---- 电平条字符 ----
BAR_FULL  = '\u25ae'   # ▮
BAR_EMPTY = '\u2591'   # ░

# ---- 电平条颜色（根据阈值分级） ----
LEVEL_GREEN  = '#00ff44'   # 低电平 (< 60/127)
LEVEL_YELLOW = '#ffff00'   # 中电平 (60~90/127)
LEVEL_RED    = '#ff4444'   # 高电平 (> 90/127)
LEVEL_EMPTY_COLOR = '#1a3a1a'


def _build_level_html(level: int) -> str:
    """构建8格电平条HTML字符串，附带dB值
    
    level: 0~127 模拟信号电平
    每格对应 127/8 约15.9 的范围，颜色按阈值分级
    """
    filled = round(level / 127.0 * 8)
    html = ''
    for i in range(8):
        # 该格对应的电平阈值
        bar_threshold = (i + 1) / 8.0 * 127.0
        if i < filled:
            if bar_threshold <= 60:
                color = LEVEL_GREEN
            elif bar_threshold <= 90:
                color = LEVEL_YELLOW
            else:
                color = LEVEL_RED
            html += f'<font color="{color}">{BAR_FULL}</font>'
        else:
            html += f'<font color="{LEVEL_EMPTY_COLOR}">{BAR_EMPTY}</font>'
    # 附加dB值
    if level == 0:
        db_str = '-inf'
    else:
        db = (level / 127.0) * 60.0 - 60.0
        db_str = f'{db:+.0f}dB'
    return f'{html}<font color="{LCD_TEXT}"> {db_str}</font>'


class LcdWidget(QFrame):
    """LCD/OLED液晶显示屏模拟控件
    
    4行内容：
      行1：通道号 + 通道名
      行2：8格电平条 + dB值（QTimer动画）
      行3：编码器当前模式 + 参数值
      行4：按键功能提示（激活时高亮黄色）
    
    支持3种显示模式：
      normal      - 正常显示
      bank        - 翻页通道选择
      calibration - 推子校准进度
    """

    def __init__(self, channel_id: int, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id

        # ---- 通道状态缓存 ----
        self._ch_num     = channel_id + 1
        self._ch_name    = f'CH{channel_id + 1}'
        self._enc_mode   = 0           # 0=COMP, 1=GATE, 2=PAN
        self._comp_thr   = -20.0       # dB
        self._gate_thr   = -40.0       # dB
        self._pan        = 0           # -63~63
        self._mute       = False
        self._solo       = False
        self._sel        = False
        self._dyn        = False

        # ---- 电平动画状态 ----
        self._level      = 0           # 当前模拟电平 0~127
        self._peak       = 0           # 峰值保持
        self._peak_hold  = 0           # 峰值保持计数器（10次=1秒）

        # ---- 显示模式 ----
        self._display_mode = 'normal'  # 'normal' | 'bank' | 'calibration'

        # ---- 电平动画定时器（100ms）----
        self._level_timer = QTimer(self)
        self._level_timer.setInterval(100)
        self._level_timer.timeout.connect(self._tick_level)
        self._level_timer.start()

        self._setup_ui()
        self._refresh()

    # ----------------------------------------------------------------
    # UI 初始化
    # ----------------------------------------------------------------
    def _setup_ui(self):
        """初始化UI布局"""
        self.setObjectName("lcdWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedSize(120, 92)   # 比原版高20px，容纳第4行

        self.setStyleSheet(f"""
            QFrame#lcdWidget {{
                background-color: {LCD_BG};
                border: 2px solid #003300;
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(1)

        # 等宽字体保持LCD风格
        font_md = QFont("Consolas", 9, QFont.Weight.Bold)
        font_sm = QFont("Consolas", 8, QFont.Weight.Bold)

        # 行1：通道号+通道名
        self.lbl1 = QLabel()
        self.lbl1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl1.setFont(font_md)
        self.lbl1.setStyleSheet(f"color: {LCD_TEXT}; background: transparent;")
        layout.addWidget(self.lbl1)

        # 行2：电平条（HTML富文本）
        self.lbl2 = QLabel()
        self.lbl2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl2.setFont(font_sm)
        self.lbl2.setTextFormat(Qt.TextFormat.RichText)
        self.lbl2.setStyleSheet("background: transparent;")
        layout.addWidget(self.lbl2)

        # 行3：编码器参数
        self.lbl3 = QLabel()
        self.lbl3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl3.setFont(font_sm)
        self.lbl3.setStyleSheet(f"color: {LCD_TEXT}; background: transparent;")
        layout.addWidget(self.lbl3)

        # 行4：按键功能提示（HTML富文本）
        self.lbl4 = QLabel()
        self.lbl4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl4.setFont(font_sm)
        self.lbl4.setTextFormat(Qt.TextFormat.RichText)
        self.lbl4.setStyleSheet("background: transparent;")
        layout.addWidget(self.lbl4)

    # ----------------------------------------------------------------
    # 电平动画
    # ----------------------------------------------------------------
    def _tick_level(self):
        """每100ms更新一次电平动画（随机模拟音频信号）"""
        if self._display_mode != 'normal':
            return

        # 随机目标电平，逐步逼近（模拟真实VU表）
        target = random.randint(0, 127)
        if target > self._level:
            self._level = min(127, self._level + random.randint(6, 18))
        else:
            self._level = max(0, self._level - random.randint(3, 10))

        # 峰值保持逻辑（10个周期 ≈ 1秒）
        if self._level > self._peak:
            self._peak = self._level
            self._peak_hold = 10
        elif self._peak_hold > 0:
            self._peak_hold -= 1
        else:
            self._peak = max(self._peak - 4, self._level)

        # 刷新第2行
        self.lbl2.setText(_build_level_html(self._level))

    # ----------------------------------------------------------------
    # 刷新逻辑
    # ----------------------------------------------------------------
    def _refresh(self):
        """根据当前显示模式刷新所有行"""
        if self._display_mode == 'normal':
            self._show_normal()

    def _show_normal(self):
        """正常状态：4行标准显示"""
        # 行1：通道号 + 通道名（最多8字符）
        ch_prefix = f'CH{self._ch_num}'
        self.lbl1.setText(f'{ch_prefix:<5}{self._ch_name[:7]}')

        # 行2：由电平定时器维护，这里只初始化
        self.lbl2.setText(_build_level_html(self._level))

        # 行3：编码器参数
        if self._enc_mode == 0:
            line3 = f'COMP{self._comp_thr:+.0f}dB'
        elif self._enc_mode == 1:
            line3 = f'GATE{self._gate_thr:+.0f}dB'
        else:
            if self._pan == 0:
                pan_str = 'C'
            elif self._pan < 0:
                pan_str = f'L{abs(self._pan)}'
            else:
                pan_str = f'R{self._pan}'
            line3 = f'PAN {pan_str:>8}'
        self.lbl3.setText(line3)

        # 行4：按键提示
        self._update_btn_hints()

    def _update_btn_hints(self):
        """更新按键功能提示行（激活时高亮）"""
        def fmt(label: str, active: bool, color: str) -> str:
            if active:
                return (f'<font color="{color}">'
                        f'[{label}]</font>')
            return f'<font color="#777777"> {label} </font>'

        m   = fmt('M',   self._mute, '#ff4444')
        s   = fmt('SL',  self._solo, '#4488ff')
        sel = fmt('SEL', self._sel,  '#ffffff')
        d   = fmt('DYN', self._dyn,  '#ff8800')
        self.lbl4.setText(f'{m}{s}{sel}{d}')

    # ----------------------------------------------------------------
    # 公开接口：正常模式更新
    # ----------------------------------------------------------------
    def set_channel_info(self, ch_num: int, ch_name: str):
        """更新通道编号和名称"""
        self._ch_num  = ch_num
        self._ch_name = ch_name
        if self._display_mode == 'normal':
            self.lbl1.setText(f'CH{ch_num:<4}{ch_name[:7]}')

    def set_encoder_state(self, mode_idx: int,
                          comp_thr: float, gate_thr: float, pan: int):
        """更新编码器模式及参数"""
        self._enc_mode  = mode_idx
        self._comp_thr  = comp_thr
        self._gate_thr  = gate_thr
        self._pan       = pan
        if self._display_mode == 'normal':
            if mode_idx == 0:
                self.lbl3.setText(f'COMP{comp_thr:+.0f}dB')
            elif mode_idx == 1:
                self.lbl3.setText(f'GATE{gate_thr:+.0f}dB')
            else:
                pan_str = 'C' if pan == 0 else (
                    f'L{abs(pan)}' if pan < 0 else f'R{pan}')
                self.lbl3.setText(f'PAN {pan_str:>8}')

    def set_button_states(self, mute: bool, solo: bool,
                          sel: bool, dyn: bool):
        """更新按键激活状态"""
        self._mute = mute
        self._solo = solo
        self._sel  = sel
        self._dyn  = dyn
        if self._display_mode == 'normal':
            self._update_btn_hints()

    # ----------------------------------------------------------------
    # 公开接口：特殊显示模式
    # ----------------------------------------------------------------
    def show_bank_mode(self, target_ch: int):
        """显示翻页通道选择界面"""
        self._display_mode = 'bank'
        self.lbl1.setText('\u25c4 CH BANK \u25ba')   # ◄ CH BANK ►
        self.lbl2.setText(
            f'<font color="{LCD_TEXT}">  &lt; CH {target_ch:3d} &gt;</font>')
        self.lbl3.setText('\u65cb\u8f6c\u9009\u901a\u9053')   # 旋转选通道
        self.lbl4.setText(
            f'<font color="#ffff00"> \u6309\u4e0b\u786e\u8ba4   </font>')  # 按下确认

    def show_calibration(self, ch_num: int, ch_name: str, progress: int):
        """显示推子校准进度"""
        self._display_mode = 'calibration'
        filled = round(progress / 100.0 * 8)
        bar = '\u2588' * filled + '\u2591' * (8 - filled)  # █ 和 ░
        self.lbl1.setText(f'>> CH{ch_num}')
        self.lbl2.setText(
            f'<font color="{LCD_TEXT}">{ch_name[:12]}</font>')
        self.lbl3.setText('\u63a8\u5b50\u6821\u51c6\u4e2d...')   # 推子校准中...
        self.lbl4.setText(
            f'<font color="#ffff00">{bar} {progress:3d}%</font>')

    def show_normal(self):
        """恢复正常显示模式"""
        self._display_mode = 'normal'
        self._refresh()

    # ----------------------------------------------------------------
    # 旧接口兼容（保留供 channel_strip.py 调用）
    # ----------------------------------------------------------------
    def set_db_value(self, db_str: str):
        """旧接口：dB值由电平动画取代，此方法空实现"""
        pass

    def set_mode(self, mode: str):
        """旧接口：由 set_encoder_state 取代，此方法空实现"""
        pass

    def set_channel_name(self, name: str):
        """旧接口：更新通道名"""
        self._ch_name = name
        if self._display_mode == 'normal':
            self._refresh()
