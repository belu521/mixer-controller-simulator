#pragma once
// firmware/src/encoder_input.h
// EC11 编码器解码接口（5路，使用 Encoder 库）
// 功能：旋转解码 + 加速检测（与 Python 模拟器的 delta 处理对应）

#include <Arduino.h>

namespace EncoderInput {

// 加速参数：两次步进间隔 < 以下 ms 时放大 delta
constexpr uint32_t ACCEL_FAST_MS = 80;   // 快速旋转判定阈值
constexpr int      ACCEL_MULT    = 4;    // 快速旋转时 delta 乘数

// 初始化（注册 5 路 Encoder 对象）
void begin();

// 轮询更新（在 loop() 中调用）
void update();

// 旋转回调（stripId 0~4，delta ±n，已含加速乘数）
using RotateCallback = void (*)(uint8_t stripId, int delta);
void onRotated(RotateCallback cb);

} // namespace EncoderInput
