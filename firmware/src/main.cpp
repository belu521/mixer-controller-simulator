// firmware/src/main.cpp
// Teensy 4.1 混音台控制器固件主入口
// 对应 Python 模拟器: main.py / mixer_simulator/

#include <Arduino.h>
#include "pin_config.h"
#include "mixer_state.h"
#include "midi_io.h"
#include "fader_driver.h"
#include "encoder_input.h"
#include "hc4067_scanner.h"
#include "button_input.h"
#include "oled_display.h"
#include "led_feedback.h"

// ──────────────────────────────────────────────────────────
// MixerState 事件回调（连接各子系统）
// ──────────────────────────────────────────────────────────

// 推子手动移动 → MixerState
static void onFaderUserMoved(uint8_t stripId, uint8_t value) {
    MixerState::onFaderMoved(stripId, value);
    OledDisplay::markDirty(stripId);
}

// 编码器旋转 → MixerState
static void onEncoderRotated(uint8_t stripId, int delta) {
    MixerState::onEncoderRotated(stripId, delta);
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：推子值变化 → 标记 OLED 刷新 + LED 更新
static void onFaderChanged(uint8_t stripId, uint8_t /*value*/) {
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：按钮状态变化
static void onButtonChanged(uint8_t stripId, const char* /*btn*/, bool /*active*/) {
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：编码器值变化
static void onEncoderValueChanged(uint8_t stripId, const char* /*val*/) {
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：编码器模式变化
static void onEncoderModeChanged(uint8_t stripId) {
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：通道切换
static void onChannelSwitched(uint8_t stripId) {
    // 切换通道后，推子需要移动到新通道的目标位置
    const MixerState::ChannelState& ch = MixerState::getStripChannel(stripId);
    FaderDriver::setTarget(stripId, ch.faderValue);
    OledDisplay::markDirty(stripId);
}

// MixerState 回调：翻页模式变化
static void onPageTurnModeChanged(uint8_t stripId) {
    OledDisplay::markDirty(stripId);
}

// MIDI 接收：CC7 远端控制推子位置
static void onCcReceived(uint8_t midiCh, uint8_t cc, uint8_t value) {
    if (cc != CC_FADER) return;
    // 找到对应的 strip（MIDI 通道 1~16 循环，匹配第一个）
    for (uint8_t i = 0; i < 5; i++) {
        const MixerState::StripState& strip = MixerState::getStrip(i);
        if (MidiIO::midiChannelOf(strip.currentChannel) == midiCh) {
            // 更新状态并驱动推子
            MixerState::getChannel(strip.currentChannel).faderValue = value;
            FaderDriver::setTarget(i, value);
            OledDisplay::markDirty(i);
            break;
        }
    }
}

// ──────────────────────────────────────────────────────────
// setup()
// ──────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(200);  // 等待串口稳定
    Serial.println("[MixerFW] Teensy 4.1 Mixer Controller starting...");

    // 初始化各子系统（顺序很重要：先状态机，再 IO）
    MidiIO::begin();
    MixerState::begin();
    FaderDriver::begin();
    EncoderInput::begin();
    HC4067Scanner::begin();
    ButtonInput::begin();
    OledDisplay::begin();   // 包含 TCA9548A 初始化和 5 块 OLED 初始化
    LedFeedback::begin();

    // 注册子系统间回调
    FaderDriver::onUserMoved(onFaderUserMoved);
    EncoderInput::onRotated(onEncoderRotated);
    MidiIO::onCcReceived(onCcReceived);

    MixerState::onFaderChanged(onFaderChanged);
    MixerState::onButtonChanged(onButtonChanged);
    MixerState::onEncoderValueChanged(onEncoderValueChanged);
    MixerState::onEncoderModeChanged(onEncoderModeChanged);
    MixerState::onChannelSwitched(onChannelSwitched);
    MixerState::onPageTurnModeChanged(onPageTurnModeChanged);

    // 启动后刷新所有显示
    OledDisplay::refreshAll();

    Serial.println("[MixerFW] setup() complete");
}

// ──────────────────────────────────────────────────────────
// loop()
// ──────────────────────────────────────────────────────────
void loop() {
    HC4067Scanner::update();    // 扫描 3 颗 HC4067（约 2ms/轮）
    EncoderInput::update();     // 轮询 5 路编码器
    FaderDriver::update();      // ADC 采样 + 电机闭环（限速 1ms）
    ButtonInput::update();      // 空轮询（回调已由 HC4067Scanner 触发）
    OledDisplay::update();      // 仅刷新被标记为 dirty 的屏幕
    LedFeedback::update();      // LED 刷新（限速 30ms）
    MidiIO::update();           // 处理接收到的 MIDI 消息
}
