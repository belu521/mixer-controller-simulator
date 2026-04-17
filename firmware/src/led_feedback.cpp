// firmware/src/led_feedback.cpp
// WS2812B LED × 25 状态反馈实现
// LED 分配方案（每 strip 5 颗）：
//   LED0: SELECT 状态 — 白/灭
//   LED1: MUTE 状态   — 红/灭
//   LED2: SOLO 状态   — 黄/灭
//   LED3: DYN 状态    — 绿/灭
//   LED4: 推子电平     — 绿→黄→红（VU 风格）

#include "led_feedback.h"
#include "pin_config.h"
#include "mixer_state.h"
#include <FastLED.h>

namespace LedFeedback {

// ──────────────────────────────────────────────────────────
// FastLED 配置
// ──────────────────────────────────────────────────────────
static CRGB _leds[PinConfig::LED_COUNT];

// 启动亮度（低，避免浪涌电流）后续运行时可提高
constexpr uint8_t STARTUP_BRIGHTNESS = 16;   // /255
constexpr uint8_t RUN_BRIGHTNESS     = 80;

// ──────────────────────────────────────────────────────────
// begin() — FastLED 初始化
// ──────────────────────────────────────────────────────────
void begin() {
    // Teensy 4.1 Pin10 → WS2812B，RGB 顺序 GRB
    FastLED.addLeds<WS2812B, PinConfig::LED_DATA_PIN, GRB>(_leds, PinConfig::LED_COUNT);
    FastLED.setBrightness(STARTUP_BRIGHTNESS);

    // 全部熄灭
    fill_solid(_leds, PinConfig::LED_COUNT, CRGB::Black);
    FastLED.show();

    // 启动完成后提高亮度
    FastLED.setBrightness(RUN_BRIGHTNESS);
}

// ──────────────────────────────────────────────────────────
// faderToVu — 推子 MIDI 值 → VU 颜色
// 0~50 → 绿；51~90 → 黄；91~127 → 红
// ──────────────────────────────────────────────────────────
static CRGB faderToVu(uint8_t midi) {
    if (midi > 90) return CRGB(200, 0, 0);       // 红
    if (midi > 50) return CRGB(200, 200, 0);     // 黄
    if (midi > 0)  return CRGB(0, 180, 0);       // 绿
    return CRGB::Black;                           // 0 = 无信号
}

// ──────────────────────────────────────────────────────────
// refresh() — 根据当前 MixerState 计算所有 LED 颜色
// ──────────────────────────────────────────────────────────
void refresh() {
    for (uint8_t s = 0; s < 5; s++) {
        const MixerState::StripState&   strip = MixerState::getStrip(s);
        const MixerState::ChannelState& ch    = MixerState::getChannel(strip.currentChannel);

        uint8_t base = s * 5;  // 该 strip 起始 LED 索引

        // LED0: SELECT（白/灭）
        _leds[base + 0] = ch.selectActive ? CRGB(80, 80, 80) : CRGB::Black;

        // LED1: MUTE（红/灭）
        _leds[base + 1] = ch.muteActive ? CRGB(180, 0, 0) : CRGB::Black;

        // LED2: SOLO（黄/灭）
        _leds[base + 2] = ch.soloActive ? CRGB(180, 180, 0) : CRGB::Black;

        // LED3: DYN（绿/灭）
        _leds[base + 3] = ch.dynActive ? CRGB(0, 160, 0) : CRGB::Black;

        // LED4: 推子电平 VU
        _leds[base + 4] = faderToVu(ch.faderValue);
    }
    FastLED.show();
}

// ──────────────────────────────────────────────────────────
// update() — 限速约 30ms 刷新一次（~33fps，不占用过多 CPU）
// ──────────────────────────────────────────────────────────
void update() {
    static uint32_t lastMs = 0;
    uint32_t now = millis();
    if (now - lastMs < 30) return;
    lastMs = now;
    refresh();
}

} // namespace LedFeedback
