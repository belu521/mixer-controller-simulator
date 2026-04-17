// firmware/src/fader_driver.cpp
// 电动推子驱动实现
// - ADC 采样（1ms 周期，IIR 滤波）
// - 电机闭环控制（死区/减速/失速保护/用户接触检测）
// - 底层 H 桥（TB6612FNG）控制

#include "fader_driver.h"
#include "pin_config.h"

namespace FaderDriver {

// ──────────────────────────────────────────────────────────
// 每个推子的运行时状态
// ──────────────────────────────────────────────────────────
struct FaderState {
    float    filtered;          // IIR 滤波后的原始 ADC 值（0~1023）
    uint8_t  midiValue;         // 当前量化 MIDI 值（0~127）
    uint8_t  prevMidi;          // 上次上报的 MIDI 值（用于滞回去抖）
    bool     hasTarget;         // 是否有闭环目标
    uint8_t  target;            // 目标 MIDI 值（0~127）
    uint32_t stallTimer;        // 失速计时起始 millis()
    uint8_t  stallLastMidi;     // 失速检测用的上次 MIDI 值
};

static FaderState _states[5];
static FaderMoveCallback _cbUserMoved = nullptr;

// ADC 满量程（Teensy 4.1 默认 10bit=1023）
constexpr float ADC_MAX = 1023.0f;

// ──────────────────────────────────────────────────────────
// 内部：原始 ADC → MIDI 值（带 1 步滞回）
// ──────────────────────────────────────────────────────────
static uint8_t adcToMidi(float adcFiltered, uint8_t prevMidi) {
    int raw = (int)(adcFiltered / ADC_MAX * 127.0f + 0.5f);
    if (raw < 0) raw = 0;
    if (raw > 127) raw = 127;
    // 滞回：±1 之内保持上次值（防止在量化边界抖动）
    if (abs(raw - (int)prevMidi) <= 1) return prevMidi;
    return (uint8_t)raw;
}

// ──────────────────────────────────────────────────────────
// begin() — 初始化引脚
// ──────────────────────────────────────────────────────────
void begin() {
    // 配置 ADC 分辨率（Teensy 4.1 支持最高 12bit；保持默认 10bit 即可）
    analogReadResolution(10);

    for (uint8_t i = 0; i < 5; i++) {
        // ADC 引脚（INPUT 即可，analogRead 会自动配置）
        pinMode(PinConfig::FADER_ADC_PINS[i], INPUT);

        // 电机引脚
        pinMode(PinConfig::MTR_PWM_PINS[i], OUTPUT);
        pinMode(PinConfig::MTR_IN1_PINS[i], OUTPUT);
        pinMode(PinConfig::MTR_IN2_PINS[i], OUTPUT);

        // 初始状态：刹车
        coast(i);

        // 读取初始 ADC
        int initAdc = analogRead(PinConfig::FADER_ADC_PINS[i]);
        _states[i].filtered    = (float)initAdc;
        _states[i].midiValue   = adcToMidi(_states[i].filtered, 0);
        _states[i].prevMidi    = _states[i].midiValue;
        _states[i].hasTarget   = false;
        _states[i].target      = _states[i].midiValue;
        _states[i].stallTimer  = 0;
        _states[i].stallLastMidi = _states[i].midiValue;
    }
}

// ──────────────────────────────────────────────────────────
// update() — 每 ~1ms 调用一次
// 1. 采样 ADC → IIR 滤波 → 量化
// 2. 若有闭环目标 → 驱动电机 + 失速检测
// 3. 若无闭环 → 检测用户手动操作
// ──────────────────────────────────────────────────────────
void update() {
    static uint32_t lastMs = 0;
    uint32_t now = millis();
    if (now - lastMs < 1) return;  // 限速 ~1ms
    lastMs = now;

    for (uint8_t i = 0; i < 5; i++) {
        FaderState& fs = _states[i];

        // ── 采样 + IIR 滤波 ──
        int raw = analogRead(PinConfig::FADER_ADC_PINS[i]);
        fs.filtered = IIR_ALPHA * (float)raw + (1.0f - IIR_ALPHA) * fs.filtered;
        uint8_t curMidi = adcToMidi(fs.filtered, fs.prevMidi);
        fs.midiValue = curMidi;

        if (fs.hasTarget) {
            // ────── 闭环控制 ──────
            int err = (int)fs.target - (int)curMidi;

            if (abs(err) <= DEAD_ZONE) {
                // 到达死区：停止并清除目标
                brake(i);
                fs.hasTarget = false;
                fs.prevMidi  = curMidi;
                continue;
            }

            // 失速检测：ADC 持续无变化
            if (curMidi != fs.stallLastMidi) {
                fs.stallLastMidi = curMidi;
                fs.stallTimer    = now;
            } else if ((now - fs.stallTimer) > STALL_TIMEOUT_MS) {
                // 失速：停止保护
                brake(i);
                fs.hasTarget = false;
                fs.prevMidi  = curMidi;
                continue;
            }

            // 用户接触检测：
            // 若推子移动方向与电机目标方向相反 → 用户在推 → 让路
            int motorDir = (err > 0) ? 1 : -1;
            int adcDelta = (int)curMidi - (int)fs.prevMidi;
            if (abs(adcDelta) >= DEAD_ZONE && adcDelta * motorDir < 0) {
                // 用户推力明显（方向与目标反） → 停止让路
                coast(i);
                fs.prevMidi = curMidi;
                continue;
            }

            // 计算 PWM（接近目标时减速）
            uint8_t pwm;
            if (abs(err) <= SOFT_ZONE) {
                // 减速区：按比例降低 PWM
                pwm = (uint8_t)((uint32_t)PWM_MAX * abs(err) / SOFT_ZONE);
            if (pwm < PWM_MIN_SOFT) pwm = PWM_MIN_SOFT;  // 最低保持防止卡顿
            } else {
                pwm = PWM_MAX;
            }

            if (err > 0) forward(i, pwm);
            else         reverse(i, pwm);

        } else {
            // ────── 无闭环：检测用户手动操作 ──────
            if (curMidi != fs.prevMidi) {
                fs.prevMidi = curMidi;
                if (_cbUserMoved) _cbUserMoved(i, curMidi);
            }
        }
    }
}

// ──────────────────────────────────────────────────────────
// setTarget / cancelTarget / getValue
// ──────────────────────────────────────────────────────────
void setTarget(uint8_t stripId, uint8_t target) {
    if (stripId >= 5) return;
    FaderState& fs    = _states[stripId];
    fs.target         = target;
    fs.hasTarget      = true;
    fs.stallTimer     = millis();
    fs.stallLastMidi  = fs.midiValue;
}

void cancelTarget(uint8_t stripId) {
    if (stripId >= 5) return;
    _states[stripId].hasTarget = false;
    coast(stripId);
}

uint8_t getValue(uint8_t stripId) {
    if (stripId >= 5) return 0;
    return _states[stripId].midiValue;
}

void onUserMoved(FaderMoveCallback cb) { _cbUserMoved = cb; }

// ──────────────────────────────────────────────────────────
// 底层 H 桥控制（TB6612FNG 真值表）
//   IN1=1, IN2=0, PWM → 正转（推子向上）
//   IN1=0, IN2=1, PWM → 反转（推子向下）
//   IN1=1, IN2=1, any → 刹车
//   IN1=0, IN2=0, 0   → 滑行
// ──────────────────────────────────────────────────────────
void forward(uint8_t stripId, uint8_t pwm) {
    if (stripId >= 5) return;
    digitalWrite(PinConfig::MTR_IN1_PINS[stripId], HIGH);
    digitalWrite(PinConfig::MTR_IN2_PINS[stripId], LOW);
    analogWrite(PinConfig::MTR_PWM_PINS[stripId], pwm);
}

void reverse(uint8_t stripId, uint8_t pwm) {
    if (stripId >= 5) return;
    digitalWrite(PinConfig::MTR_IN1_PINS[stripId], LOW);
    digitalWrite(PinConfig::MTR_IN2_PINS[stripId], HIGH);
    analogWrite(PinConfig::MTR_PWM_PINS[stripId], pwm);
}

void brake(uint8_t stripId) {
    if (stripId >= 5) return;
    digitalWrite(PinConfig::MTR_IN1_PINS[stripId], HIGH);
    digitalWrite(PinConfig::MTR_IN2_PINS[stripId], HIGH);
    analogWrite(PinConfig::MTR_PWM_PINS[stripId], 0);
}

void coast(uint8_t stripId) {
    if (stripId >= 5) return;
    digitalWrite(PinConfig::MTR_IN1_PINS[stripId], LOW);
    digitalWrite(PinConfig::MTR_IN2_PINS[stripId], LOW);
    analogWrite(PinConfig::MTR_PWM_PINS[stripId], 0);
}

} // namespace FaderDriver
