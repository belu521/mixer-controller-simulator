#pragma once
// firmware/src/led_feedback.h
// WS2812B LED × 25 状态反馈接口（5 strip × 5 颗/strip）

#include <Arduino.h>

namespace LedFeedback {

// 初始化（FastLED 配置，低亮度启动避免浪涌电流）
void begin();

// 周期更新（根据 MixerState 刷新 LED 颜色）
void update();

// 强制立即刷新所有 LED
void refresh();

} // namespace LedFeedback
