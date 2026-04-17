#pragma once
// firmware/src/hc4067_scanner.h
// HC4067 × 3 多路复用器扫描接口
// 扫描频率 ~500Hz，提供单击/双击/长按事件检测

#include <Arduino.h>

namespace HC4067Scanner {

constexpr uint8_t NUM_CHIPS    = 3;   // HC4067 数量
constexpr uint8_t NUM_CHANNELS = 16;  // 每颗 16 路

// 事件类型
enum class Event : uint8_t {
    PRESS      = 0,  // 按下（可用于实时检测）
    RELEASE    = 1,  // 释放
    CLICK      = 2,  // 单击（≤200ms 内释放）
    DOUBLE     = 3,  // 双击（300ms 内两次单击）
    LONG_PRESS = 4,  // 长按（≥500ms 持续按下）
};

// 时间阈值（ms）
constexpr uint32_t CLICK_MAX_MS    = 200;  // 单击最长按压时间
constexpr uint32_t DOUBLE_GAP_MS   = 300;  // 双击最大间隔
constexpr uint32_t LONG_PRESS_MS   = 500;  // 长按判定时间

// 事件回调：(chip 0~2, channel 0~15, event)
using EventCallback = void (*)(uint8_t chip, uint8_t channel, Event event);

// 初始化
void begin();

// 轮询更新（在 loop() 中调用，~2ms 扫描一轮）
void update();

// 获取通道当前电平（true=按下/低电平）
bool getChannelState(uint8_t chip, uint8_t channel);

// 注册事件回调
void onEvent(EventCallback cb);

} // namespace HC4067Scanner
