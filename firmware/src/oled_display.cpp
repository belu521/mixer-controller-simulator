// firmware/src/oled_display.cpp
// OLED 显示实现
// - TCA9548A I2C 多路复用（0x70）
// - 5 块 SSD1306 128×64（共享 Wire，分通道访问）
// - 正常页面 + CH BANK 翻页页面

#include "oled_display.h"
#include "pin_config.h"
#include "default_names.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

namespace OledDisplay {

// ──────────────────────────────────────────────────────────
// OLED 参数
// ──────────────────────────────────────────────────────────
constexpr uint8_t OLED_W   = 128;
constexpr uint8_t OLED_H   = 64;
constexpr int8_t  OLED_RST = -1;   // 无硬件复位脚（使用软复位）

// 5 块 SSD1306 实例（共享 Wire，由 TCA9548A 通道选择）
static Adafruit_SSD1306 _disp[5] = {
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
};

// 脏标记（哪块屏需要刷新）
static bool _dirty[5] = { true, true, true, true, true };

// ──────────────────────────────────────────────────────────
// TCA9548A 通道切换
// 写地址 0x70，数据 = 1 << ch（选中通道 0~4）
// ──────────────────────────────────────────────────────────
static void selectTcaChannel(uint8_t ch) {
    Wire.beginTransmission(PinConfig::TCA9548A_ADDR);
    Wire.write(1 << ch);
    Wire.endTransmission();
}

// ──────────────────────────────────────────────────────────
// midi_to_db — 对应 fader_widget.py 第 20~26 行
// 输入 MIDI 值 0~127 → 返回 dB 字符串（写入 buf，bufLen 含 '\0'）
// ──────────────────────────────────────────────────────────
static void midiToDb(uint8_t midi, char* buf, uint8_t bufLen) {
    if (midi == 0) {
        strncpy(buf, "-inf dB", bufLen);
        buf[bufLen - 1] = '\0';
        return;
    }
    // 线性映射：127→+13.5dB, 100→0.0dB, 0→-inf
    // db = (midi - 100) * 0.5
    // 对应 fader_widget.py 第 20~26 行
    if (midi == 100) {
        strncpy(buf, "0.0dB", bufLen);
        buf[bufLen - 1] = '\0';
        return;
    }
    float db = (float)((int)midi - 100) * 0.5f;
    if (db > 0.0f) {
        snprintf(buf, bufLen, "+%.1fdB", (double)db);
    } else {
        snprintf(buf, bufLen, "%.1fdB", (double)db);
    }
}

// ──────────────────────────────────────────────────────────
// begin() — 初始化 Wire + TCA9548A + 5 块 OLED
// ──────────────────────────────────────────────────────────
void begin() {
    Wire.begin();
    Wire.setClock(400000);  // 400kHz Fast Mode

    for (uint8_t i = 0; i < 5; i++) {
        selectTcaChannel(i);
        if (!_disp[i].begin(SSD1306_SWITCHCAPVCC, PinConfig::OLED_ADDR)) {
            Serial.print("[OledDisplay] OLED ");
            Serial.print(i + 1);
            Serial.println(" init failed");
        } else {
            _disp[i].clearDisplay();
            _disp[i].setTextColor(SSD1306_WHITE);
            _disp[i].display();
        }
    }
    Serial.println("[OledDisplay] all OLEDs initialized");
}

// ──────────────────────────────────────────────────────────
// 渲染并推送到指定屏（先切 TCA9548A 通道）
// ──────────────────────────────────────────────────────────
static void flushDisplay(uint8_t stripId) {
    selectTcaChannel(stripId);
    _disp[stripId].display();
}

// ──────────────────────────────────────────────────────────
// renderNormal — 正常显示页面
// ┌──────────────────────┐
// │ CH1  Kick Drm        │  行0  文字高8px
// │ ████████  -6.0dB     │  行1  推子条+dB
// │ COMP -20.0dB         │  行2  编码器模式+值
// │ [M] SL [SEL] [DYN]   │  行3  4按钮状态
// └──────────────────────┘
// ──────────────────────────────────────────────────────────
void renderNormal(uint8_t stripId, const ChannelState& ch) {
    Adafruit_SSD1306& d = _disp[stripId];
    d.clearDisplay();
    d.setTextSize(1);

    // 行 0：通道号 + 名称
    d.setCursor(0, 0);
    d.print("CH");
    d.print(ch.chNum);
    d.print("  ");
    d.print(ch.name);

    // 行 1：推子进度条（0~127 → 宽度 0~80px）+ dB 值
    d.setCursor(0, 10);
    uint8_t barW = (uint8_t)((uint16_t)ch.faderValue * 80 / 127);
    d.fillRect(0, 12, barW, 8, SSD1306_WHITE);  // 填充进度条
    d.drawRect(0, 12, 80, 8, SSD1306_WHITE);     // 进度条边框
    char dbStr[12];
    midiToDb(ch.faderValue, dbStr, sizeof(dbStr));
    d.setCursor(84, 12);
    d.print(dbStr);

    // 行 2：编码器模式 + 当前值
    d.setCursor(0, 24);
    const char* modeNames[] = { "COMP", "GATE", "PAN" };
    d.print(modeNames[ch.encoderModeIndex]);
    d.print(" ");
    char valStr[16];
    switch (ch.encoderModeIndex) {
        case 0:  // COMP
            snprintf(valStr, sizeof(valStr), "%.1fdB", (double)ch.compThr);
            break;
        case 1:  // GATE
            snprintf(valStr, sizeof(valStr), "%.1fdB", (double)ch.gateThr);
            break;
        default: // PAN
            if (ch.pan < 0)
                snprintf(valStr, sizeof(valStr), "L%d", -ch.pan);
            else if (ch.pan > 0)
                snprintf(valStr, sizeof(valStr), "R%d", ch.pan);
            else
                strncpy(valStr, "C", sizeof(valStr));
            break;
    }
    d.print(valStr);

    // 行 3：按钮状态（激活=反白方块；未激活=普通文字）
    // M | SL | SEL | DYN
    d.setCursor(0, 40);

    // MUTE
    if (ch.muteActive) {
        d.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
        d.print("  M  ");
        d.setTextColor(SSD1306_WHITE);
    } else {
        d.print("  M  ");
    }

    // SOLO
    if (ch.soloActive) {
        d.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
        d.print(" SL  ");
        d.setTextColor(SSD1306_WHITE);
    } else {
        d.print(" SL  ");
    }

    // SELECT
    if (ch.selectActive) {
        d.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
        d.print("SEL  ");
        d.setTextColor(SSD1306_WHITE);
    } else {
        d.print("SEL  ");
    }

    // DYN
    if (ch.dynActive) {
        d.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
        d.print("[DYN]");
        d.setTextColor(SSD1306_WHITE);
    } else {
        d.print(" DYN ");
    }

    flushDisplay(stripId);
}

// ──────────────────────────────────────────────────────────
// renderChannelBank — 翻页模式页面
// ┌──────────────────────┐
// │ ◄ CH BANK ►          │
// │                      │
// │      < CH1 >         │
// │                      │
// │  Rotate:select       │
// │  Click:confirm        │
// └──────────────────────┘
// ──────────────────────────────────────────────────────────
void renderChannelBank(uint8_t stripId, uint8_t targetCh) {
    Adafruit_SSD1306& d = _disp[stripId];
    d.clearDisplay();
    d.setTextSize(1);
    d.setTextColor(SSD1306_WHITE);

    // 标题行
    d.setCursor(0, 0);
    d.print("< CH BANK >");

    // 当前选中目标通道（大字）
    d.setTextSize(2);
    char chStr[12];
    snprintf(chStr, sizeof(chStr), "CH%d", (int)targetCh);
    // 居中：每字符宽 12px（size=2），行宽 128px
    uint8_t strLen = (uint8_t)strlen(chStr);
    uint8_t cx     = (128 - strLen * 12) / 2;
    d.setCursor(cx, 22);
    d.print(chStr);
    d.setTextSize(1);

    // 提示行
    d.setCursor(4, 46);
    d.print("Rotate:select");
    d.setCursor(4, 56);
    d.print("Click :confirm");

    flushDisplay(stripId);
}

// ──────────────────────────────────────────────────────────
// markDirty / refreshAll / update
// ──────────────────────────────────────────────────────────
void markDirty(uint8_t stripId) {
    if (stripId < 5) _dirty[stripId] = true;
}

void refreshAll() {
    for (uint8_t i = 0; i < 5; i++) _dirty[i] = true;
}

void update() {
    for (uint8_t i = 0; i < 5; i++) {
        if (!_dirty[i]) continue;
        _dirty[i] = false;

        const MixerState::StripState&   strip = MixerState::getStrip(i);
        const MixerState::ChannelState& ch    = MixerState::getChannel(strip.currentChannel);

        if (strip.pageTurnMode) {
            renderChannelBank(i, strip.pageTurnTarget);
        } else {
            renderNormal(i, ch);
        }
    }
}

} // namespace OledDisplay
