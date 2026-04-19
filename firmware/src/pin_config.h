#pragma once
// firmware/src/pin_config.h
// 所有引脚常量定义（严格按硬件接线最终确认版本）
// 对应文档: firmware/HARDWARE.md

#include <Arduino.h>

namespace PinConfig {

// ─────────────────────────────────────────────────────
// 推子 ADC × 5（电位器 Wiper，0~3.3V → 0~127）
// ─────────────────────────────────────────────────────
constexpr uint8_t FADER1_ADC = 14;   // A0 - Fader1 Wiper
constexpr uint8_t FADER2_ADC = 15;   // A1 - Fader2 Wiper
constexpr uint8_t FADER3_ADC = 16;   // A2 - Fader3 Wiper
constexpr uint8_t FADER4_ADC = 17;   // A3 - Fader4 Wiper
constexpr uint8_t FADER5_ADC = 20;   // A6 - Fader5 Wiper

constexpr uint8_t FADER_ADC_PINS[5] = {
    FADER1_ADC, FADER2_ADC, FADER3_ADC, FADER4_ADC, FADER5_ADC
};

// ─────────────────────────────────────────────────────
// 电机控制 × 5（TB6612FNG, VM=10V, STBY/VCC=3.3V）
// ─────────────────────────────────────────────────────

// Fader1 - TB6612_1 A通道
constexpr uint8_t MTR1_PWM = 23;  // TB6612_1 PWMA
constexpr uint8_t MTR1_IN1 = 41;  // TB6612_1 AIN1
constexpr uint8_t MTR1_IN2 = 40;  // TB6612_1 AIN2

// Fader2 - TB6612_1 B通道（BIN1=Pin38, BIN2=Pin39，已按最终接线图确认）
constexpr uint8_t MTR2_PWM = 22;  // TB6612_1 PWMB
constexpr uint8_t MTR2_IN1 = 38;  // TB6612_1 BIN1
constexpr uint8_t MTR2_IN2 = 39;  // TB6612_1 BIN2

// Fader3 - TB6612_2 A通道
constexpr uint8_t MTR3_PWM = 21;  // TB6612_2 PWMA
constexpr uint8_t MTR3_IN1 = 37;  // TB6612_2 AIN1
constexpr uint8_t MTR3_IN2 = 36;  // TB6612_2 AIN2

// Fader4 - TB6612_2 B通道
constexpr uint8_t MTR4_PWM = 13;  // TB6612_2 PWMB
constexpr uint8_t MTR4_IN1 = 35;  // TB6612_2 BIN1
constexpr uint8_t MTR4_IN2 = 34;  // TB6612_2 BIN2

// Fader5 - TB6612_3 A通道
constexpr uint8_t MTR5_PWM = 31;  // TB6612_3 PWMA
constexpr uint8_t MTR5_IN1 = 32;  // TB6612_3 AIN1
constexpr uint8_t MTR5_IN2 = 33;  // TB6612_3 AIN2

// 电机引脚数组（按推子顺序 0~4）
constexpr uint8_t MTR_PWM_PINS[5] = { MTR1_PWM, MTR2_PWM, MTR3_PWM, MTR4_PWM, MTR5_PWM };
constexpr uint8_t MTR_IN1_PINS[5] = { MTR1_IN1, MTR2_IN1, MTR3_IN1, MTR4_IN1, MTR5_IN1 };
constexpr uint8_t MTR_IN2_PINS[5] = { MTR1_IN2, MTR2_IN2, MTR3_IN2, MTR4_IN2, MTR5_IN2 };

// ─────────────────────────────────────────────────────
// 编码器 × 5（EC11，A/B 直连 Teensy，100nF+10kΩ 硬件去抖）
// ─────────────────────────────────────────────────────
constexpr uint8_t ENC1_A = 0;   // Encoder1 A相
constexpr uint8_t ENC1_B = 1;   // Encoder1 B相
constexpr uint8_t ENC2_A = 2;   // Encoder2 A相
constexpr uint8_t ENC2_B = 3;   // Encoder2 B相
constexpr uint8_t ENC3_A = 4;   // Encoder3 A相
constexpr uint8_t ENC3_B = 5;   // Encoder3 B相
constexpr uint8_t ENC4_A = 6;   // Encoder4 A相
constexpr uint8_t ENC4_B = 7;   // Encoder4 B相
constexpr uint8_t ENC5_A = 8;   // Encoder5 A相
constexpr uint8_t ENC5_B = 9;   // Encoder5 B相

constexpr uint8_t ENC_A_PINS[5] = { ENC1_A, ENC2_A, ENC3_A, ENC4_A, ENC5_A };
constexpr uint8_t ENC_B_PINS[5] = { ENC1_B, ENC2_B, ENC3_B, ENC4_B, ENC5_B };

// ─────────────────────────────────────────────────────
// HC4067 × 3（16路多路复用器，共享 S0~S3 选择脚）
// ─────────────────────────────────────────────────────
constexpr uint8_t HC4067_S0 = 26;   // 共享选择脚 S0（所有 HC4067 共用）
constexpr uint8_t HC4067_S1 = 27;   // 共享选择脚 S1
constexpr uint8_t HC4067_S2 = 28;   // 共享选择脚 S2
constexpr uint8_t HC4067_S3 = 29;   // 共享选择脚 S3

constexpr uint8_t HC4067_1_SIG = 11;  // HC4067_1 信号输出（编码器按键 + Strip1~3 按钮）
constexpr uint8_t HC4067_2_SIG = 12;  // HC4067_2 信号输出（Strip3 DYN + Strip4~5 按钮）
constexpr uint8_t HC4067_3_SIG = 24;  // HC4067_3 信号输出（全部备用）

constexpr uint8_t HC4067_SIG_PINS[3] = { HC4067_1_SIG, HC4067_2_SIG, HC4067_3_SIG };

// ─────────────────────────────────────────────────────
// I2C（TCA9548A + SSD1315 OLED × 5）
// ─────────────────────────────────────────────────────
constexpr uint8_t I2C_SDA = 18;  // I2C SDA（4.7kΩ 上拉至 3.3V）
constexpr uint8_t I2C_SCL = 19;  // I2C SCL（4.7kΩ 上拉至 3.3V）

constexpr uint8_t TCA9548A_ADDR = 0x70;  // TCA9548A I2C 地址
constexpr uint8_t OLED_ADDR     = 0x3C;  // SSD1315 I2C 地址（兼容 SSD1306）

// ─────────────────────────────────────────────────────
// WS2812B LED × 25
// ─────────────────────────────────────────────────────
constexpr uint8_t LED_DATA_PIN = 10;  // Pin10 → 330Ω → LED1 DIN
constexpr uint8_t LED_COUNT    = 25;  // 5 strip × 5 颗/strip

} // namespace PinConfig
