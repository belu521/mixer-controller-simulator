// firmware/src/encoder_input.cpp
// EC11 编码器解码实现
// 使用 Paul Stoffregen 的 Encoder 库（platformio.ini 已声明依赖）
// 加速检测：短时间内连续旋转 → delta × ACCEL_MULT

#include "encoder_input.h"
#include "pin_config.h"
#include <Encoder.h>

namespace EncoderInput {

// ──────────────────────────────────────────────────────────
// 5 路 Encoder 对象（使用中断引脚；Teensy 4.1 所有数字引脚均支持中断）
// ──────────────────────────────────────────────────────────
static Encoder* _enc[5];

static int32_t  _lastPos[5];       // 上次读取的编码器计数（Encoder 库内部为 ×4）
static uint32_t _lastStepMs[5];    // 上次步进时间戳（用于加速检测）
static RotateCallback _cbRotate = nullptr;

void begin() {
    // 动态创建 Encoder 对象（Encoder 库要求在全局/静态生命周期内存在）
    // Teensy 4.1 的堆足够大，但为了安全使用静态对象池
    static Encoder enc0(PinConfig::ENC1_A, PinConfig::ENC1_B);
    static Encoder enc1(PinConfig::ENC2_A, PinConfig::ENC2_B);
    static Encoder enc2(PinConfig::ENC3_A, PinConfig::ENC3_B);
    static Encoder enc3(PinConfig::ENC4_A, PinConfig::ENC4_B);
    static Encoder enc4(PinConfig::ENC5_A, PinConfig::ENC5_B);

    _enc[0] = &enc0;
    _enc[1] = &enc1;
    _enc[2] = &enc2;
    _enc[3] = &enc3;
    _enc[4] = &enc4;

    for (uint8_t i = 0; i < 5; i++) {
        _lastPos[i]    = _enc[i]->read();
        _lastStepMs[i] = 0;
    }
}

void update() {
    uint32_t now = millis();

    for (uint8_t i = 0; i < 5; i++) {
        int32_t pos = _enc[i]->read();
        // Encoder 库：4 计数 = 1 物理齿格（EC11 一般为 4 相位/齿）
        int32_t diff = (pos - _lastPos[i]) / 4;

        if (diff != 0) {
            _lastPos[i] += diff * 4;

            // 加速：上次步进到现在间隔短 → 乘以倍率
            int scaledDelta = diff;
            if ((now - _lastStepMs[i]) < ACCEL_FAST_MS) {
                scaledDelta *= ACCEL_MULT;
            }
            _lastStepMs[i] = now;

            if (_cbRotate) _cbRotate(i, scaledDelta);
        }
    }
}

void onRotated(RotateCallback cb) { _cbRotate = cb; }

} // namespace EncoderInput
