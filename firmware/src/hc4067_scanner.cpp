// firmware/src/hc4067_scanner.cpp
// HC4067 × 3 扫描实现
// - 共享 S0~S3 选择脚，各芯片独立 SIG 引脚
// - 扫描间隔 ~2ms（每通道 ≥ 5µs 稳定时间）
// - 单击/双击/长按状态机（每路独立）

#include "hc4067_scanner.h"
#include "pin_config.h"

namespace HC4067Scanner {

// ──────────────────────────────────────────────────────────
// 每路通道的去抖 + 事件检测状态
// ──────────────────────────────────────────────────────────
struct ChState {
    bool     raw;            // 原始读值（true=按下）
    bool     debounced;      // 去抖后状态
    uint8_t  debounceCount;  // 连续一致计数（≥3 次才翻转）

    // 事件检测
    uint32_t pressTime;      // 按下时刻
    bool     pressed;        // 当前是否按下
    bool     longSent;       // 长按事件已发送过
    uint32_t lastClickTime;  // 上次单击释放时刻（双击检测用）
    uint8_t  clickCount;     // 本轮点击次数（0/1/2）
};

static ChState    _chState[NUM_CHIPS][NUM_CHANNELS];
static bool       _rawState[NUM_CHIPS][NUM_CHANNELS];  // 最新扫描结果
static EventCallback _cbEvent = nullptr;

// ──────────────────────────────────────────────────────────
// begin() — 初始化引脚
// ──────────────────────────────────────────────────────────
void begin() {
    // S0~S3 选择脚 → 输出
    pinMode(PinConfig::HC4067_S0, OUTPUT);
    pinMode(PinConfig::HC4067_S1, OUTPUT);
    pinMode(PinConfig::HC4067_S2, OUTPUT);
    pinMode(PinConfig::HC4067_S3, OUTPUT);

    // SIG 引脚 → 输入（按键对地，上拉读高=释放）
    for (uint8_t c = 0; c < NUM_CHIPS; c++) {
        pinMode(PinConfig::HC4067_SIG_PINS[c], INPUT_PULLUP);
    }

    // 初始化状态
    for (uint8_t c = 0; c < NUM_CHIPS; c++) {
        for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
            _chState[c][ch] = { false, false, 0, 0, false, false, 0, 0 };
            _rawState[c][ch] = false;
        }
    }
}

// ──────────────────────────────────────────────────────────
// 扫描单次（选择通道 ch，读取所有 3 颗芯片）
// ──────────────────────────────────────────────────────────
static void scanChannel(uint8_t ch) {
    // 设置 S0~S3
    digitalWrite(PinConfig::HC4067_S0, (ch >> 0) & 1);
    digitalWrite(PinConfig::HC4067_S1, (ch >> 1) & 1);
    digitalWrite(PinConfig::HC4067_S2, (ch >> 2) & 1);
    digitalWrite(PinConfig::HC4067_S3, (ch >> 3) & 1);

    // ≥5µs 稳定时间
    delayMicroseconds(6);

    // 读取各芯片 SIG（低电平=按下，因为按键对 GND + 上拉）
    for (uint8_t c = 0; c < NUM_CHIPS; c++) {
        _rawState[c][ch] = (digitalRead(PinConfig::HC4067_SIG_PINS[c]) == LOW);
    }
}

// ──────────────────────────────────────────────────────────
// 事件状态机（每路通道独立）
// ──────────────────────────────────────────────────────────
static void processEvents(uint8_t chip, uint8_t ch, bool nowPressed) {
    ChState&  s   = _chState[chip][ch];
    uint32_t  now = millis();

    // ── 软件去抖（连续 3 次一致才更新 debounced） ──
    if (nowPressed == s.debounced) {
        s.debounceCount = 0;
    } else {
        s.debounceCount++;
        if (s.debounceCount >= 3) {
            s.debounced     = nowPressed;
            s.debounceCount = 0;
        }
    }

    bool cur = s.debounced;

    // ── 按下边沿 ──
    if (cur && !s.pressed) {
        s.pressed   = true;
        s.pressTime = now;
        s.longSent  = false;
        if (_cbEvent) _cbEvent(chip, ch, Event::PRESS);
    }

    // ── 持续按下：检测长按 ──
    if (s.pressed && !s.longSent && (now - s.pressTime) >= LONG_PRESS_MS) {
        s.longSent = true;
        if (_cbEvent) _cbEvent(chip, ch, Event::LONG_PRESS);
    }

    // ── 释放边沿 ──
    if (!cur && s.pressed) {
        s.pressed = false;
        uint32_t dur = now - s.pressTime;
        if (_cbEvent) _cbEvent(chip, ch, Event::RELEASE);

        if (!s.longSent && dur <= CLICK_MAX_MS) {
            // 可能是单击或双击的第二击
            if (s.clickCount == 1 && (now - s.lastClickTime) <= DOUBLE_GAP_MS) {
                // 双击
                s.clickCount     = 0;
                s.lastClickTime  = 0;
                if (_cbEvent) _cbEvent(chip, ch, Event::DOUBLE);
            } else {
                // 计数第一击，等待看是否有第二击
                s.clickCount    = 1;
                s.lastClickTime = now;
            }
        } else {
            s.clickCount    = 0;
            s.lastClickTime = 0;
        }
    }

    // ── 双击等待超时 → 确认为单击 ──
    if (s.clickCount == 1 && (now - s.lastClickTime) > DOUBLE_GAP_MS) {
        s.clickCount    = 0;
        s.lastClickTime = 0;
        if (_cbEvent) _cbEvent(chip, ch, Event::CLICK);
    }
}

// ──────────────────────────────────────────────────────────
// update() — 扫描所有 16 路 × 3 芯片（~2ms 完成一轮）
// ──────────────────────────────────────────────────────────
void update() {
    for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
        scanChannel(ch);
        for (uint8_t c = 0; c < NUM_CHIPS; c++) {
            processEvents(c, ch, _rawState[c][ch]);
        }
    }
}

// ──────────────────────────────────────────────────────────
// getChannelState
// ──────────────────────────────────────────────────────────
bool getChannelState(uint8_t chip, uint8_t channel) {
    if (chip >= NUM_CHIPS || channel >= NUM_CHANNELS) return false;
    return _chState[chip][channel].debounced;
}

void onEvent(EventCallback cb) { _cbEvent = cb; }

} // namespace HC4067Scanner
