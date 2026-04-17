#pragma once
// firmware/src/oled_display.h
// OLED × 5 显示接口（SSD1306 0x3C，经 TCA9548A 0x70）
// 实现正常页面 + CH BANK 翻页页面

#include <Arduino.h>
#include "mixer_state.h"

namespace OledDisplay {

// 初始化（Wire + TCA9548A + 5 块 SSD1306）
void begin();

// 周期更新（仅在状态变化时刷新对应屏）
void update();

// 标记指定 strip 的屏幕需要刷新（由 MixerState 回调触发）
void markDirty(uint8_t stripId);

// 强制刷新全部屏幕
void refreshAll();

/**
 * 渲染正常页面
 * ┌──────────────────────┐
 * │ CH1  Kick Drm        │  ← 通道号 + 名称
 * │ ████████  -6.0dB     │  ← 推子进度条 + dB 值
 * │ COMP -20.0dB         │  ← 编码器模式 + 值
 * │ [M] [SL] SEL [DYN]   │  ← 按钮状态（激活=反白）
 * └──────────────────────┘
 */
void renderNormal(uint8_t stripId, const ChannelState& ch);

/**
 * 渲染翻页模式页面（CH BANK）
 * ┌──────────────────────┐
 * │ ◄ CH BANK ►          │
 * │                      │
 * │      < CH1 >         │  ← 当前目标通道
 * │                      │
 * │  旋转选通道           │
 * │  按下确认             │
 * └──────────────────────┘
 */
void renderChannelBank(uint8_t stripId, uint8_t targetCh);

} // namespace OledDisplay
