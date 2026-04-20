#pragma once
// firmware/src/hc4067_scanner.h
// HC4067 × NUM_HC4067 多路复用器扫描接口
// 扫描频率 ~500Hz，提供单击/双击/长按事件检测
// 最终硬件安装 2 片（HC4067_1 + HC4067_2），HC4067_3 已取消

#include <Arduino.h>

namespace HC4067Scanner {

// 编译期常量：当前安装的 HC4067 数量（可扩展，最大 = 硬件 SIG 脚数量）
constexpr uint8_t NUM_HC4067   = 2;   // 最终硬件：HC4067_1 (Pin11) + HC4067_2 (Pin12)
constexpr uint8_t NUM_CHIPS    = NUM_HC4067;  // 内部使用别名（等价 NUM_HC4067，保持代码一致性）
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
