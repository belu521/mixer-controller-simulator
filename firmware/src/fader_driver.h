#pragma once
// firmware/src/fader_driver.h
// 电动推子驱动头文件：ADC 采样 + IIR 滤波 + 电机闭环控制
// 包含用户接触检测、失速保护、接近目标减速

#include <Arduino.h>

namespace FaderDriver {

// PWM 上限（0~255），默认 220（=约 86%，留余量避免过热）
constexpr uint8_t PWM_MAX = 220;

// 死区（ADC 量化步，等价 MIDI 值 ±2）
constexpr uint8_t DEAD_ZONE = 2;

// 失速超时（ms）：ADC 在此时间内无变化则视为失速并停止
constexpr uint32_t STALL_TIMEOUT_MS = 500;

// IIR 滤波系数（α=0.2：新值 = α*新采样 + (1-α)*旧值）
constexpr float IIR_ALPHA = 0.2f;

// 接近目标时减速区间（MIDI 值，进入此区间后 PWM 按比例降低）
constexpr uint8_t SOFT_ZONE = 15;  // 约 1/8 行程

// 初始化所有推子引脚和 ADC
void begin();

// 周期更新（在 loop() 中调用，每次 ~1ms）
void update();

/**
 * 设置推子闭环目标值（0~127）
 * @param stripId 推子编号 0~4
 * @param target  目标 MIDI 值 0~127
 */
void setTarget(uint8_t stripId, uint8_t target);

/**
 * 取消闭环控制（停止电机，等待用户手动）
 */
void cancelTarget(uint8_t stripId);

/**
 * 获取推子当前 MIDI 值（经过滤波+量化）
 */
uint8_t getValue(uint8_t stripId);

// 用户手动移动推子时的回调（stripId, midiValue）
using FaderMoveCallback = void (*)(uint8_t stripId, uint8_t value);
void onUserMoved(FaderMoveCallback cb);

// ──── 底层 H 桥控制（供测试/调试用）────

/** 正转（推子向上） */
void forward(uint8_t stripId, uint8_t pwm);

/** 反转（推子向下） */
void reverse(uint8_t stripId, uint8_t pwm);

/** 刹车（短路制动） */
void brake(uint8_t stripId);

/** 滑行（断开） */
void coast(uint8_t stripId);

} // namespace FaderDriver
