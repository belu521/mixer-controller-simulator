// firmware/src/button_input.cpp
// 按键输入映射实现
// 把 HC4067 扫描结果映射到 MixerState 方法调用
//
// 接线映射（最终确认版）：
// ┌───────────────────────────────────────────────────────┐
// │ HC4067_1 (SIG=Pin11)                                  │
// │  C0  → ENC1_SW     C1  → ENC2_SW   C2  → ENC3_SW    │
// │  C3  → ENC4_SW     C4  → ENC5_SW                     │
// │  C5  → Strip1 MUTE  C6  → Strip1 SOLO                │
// │  C7  → Strip1 SEL   C8  → Strip1 DYN                 │
// │  C9  → Strip2 MUTE  C10 → Strip2 SOLO                │
// │  C11 → Strip2 SEL   C12 → Strip2 DYN                 │
// │  C13 → Strip3 MUTE  C14 → Strip3 SOLO                │
// │  C15 → Strip3 SEL                                     │
// │ HC4067_2 (SIG=Pin12)                                  │
// │  C0  → Strip3 DYN                                     │
// │  C1  → Strip4 MUTE  C2  → Strip4 SOLO                │
// │  C3  → Strip4 SEL   C4  → Strip4 DYN                 │
// │  C5  → Strip5 MUTE  C6  → Strip5 SOLO                │
// │  C7  → Strip5 SEL   C8  → Strip5 DYN                 │
// │  C9~C15 预留备用，PCB 上不焊按键，固件不扫描（直接忽略）  │
// │ HC4067_3 — 已从最终硬件移除（不安装），固件已清理        │
// └───────────────────────────────────────────────────────┘

#include "button_input.h"
#include "hc4067_scanner.h"
#include "mixer_state.h"

namespace ButtonInput {

// ──────────────────────────────────────────────────────────
// HC4067 事件路由
// ──────────────────────────────────────────────────────────
static void onHC4067Event(uint8_t chip, uint8_t ch, HC4067Scanner::Event ev) {
    using Event = HC4067Scanner::Event;

    // 仅响应单击和双击
    bool isClick  = (ev == Event::CLICK);
    bool isDouble = (ev == Event::DOUBLE);

    if (!isClick && !isDouble) return;

    // ──────────────────────────────────────────
    // HC4067_1：编码器按键 + Strip1~3 按钮
    // ──────────────────────────────────────────
    if (chip == 0) {
        // C0~C4 → 编码器 1~5 按键
        if (ch <= 4) {
            uint8_t stripId = ch;  // ENC{n} 对应 Strip{n}（0-indexed）
            if (isDouble) {
                MixerState::onEncoderDoubleClicked(stripId);
            } else {
                MixerState::onEncoderClicked(stripId);
            }
            return;
        }
        // C5~C8 → Strip1（index=0）MUTE/SOLO/SELECT/DYN
        if (ch == 5)  { MixerState::onMuteClicked(0);   return; }
        if (ch == 6)  { MixerState::onSoloClicked(0);   return; }
        if (ch == 7)  { MixerState::onSelectClicked(0); return; }
        if (ch == 8)  { MixerState::onDynClicked(0);    return; }
        // C9~C12 → Strip2（index=1）
        if (ch == 9)  { MixerState::onMuteClicked(1);   return; }
        if (ch == 10) { MixerState::onSoloClicked(1);   return; }
        if (ch == 11) { MixerState::onSelectClicked(1); return; }
        if (ch == 12) { MixerState::onDynClicked(1);    return; }
        // C13~C15 → Strip3（index=2）MUTE/SOLO/SELECT
        if (ch == 13) { MixerState::onMuteClicked(2);   return; }
        if (ch == 14) { MixerState::onSoloClicked(2);   return; }
        if (ch == 15) { MixerState::onSelectClicked(2); return; }
    }

    // ──────────────────────────────────────────
    // HC4067_2：Strip3 DYN + Strip4~5 按钮
    // ──────────────────────────────────────────
    if (chip == 1) {
        // C0 → Strip3（index=2）DYN
        if (ch == 0)  { MixerState::onDynClicked(2);    return; }
        // C1~C4 → Strip4（index=3）MUTE/SOLO/SELECT/DYN
        if (ch == 1)  { MixerState::onMuteClicked(3);   return; }
        if (ch == 2)  { MixerState::onSoloClicked(3);   return; }
        if (ch == 3)  { MixerState::onSelectClicked(3); return; }
        if (ch == 4)  { MixerState::onDynClicked(3);    return; }
        // C5~C8 → Strip5（index=4）MUTE/SOLO/SELECT/DYN
        if (ch == 5)  { MixerState::onMuteClicked(4);   return; }
        if (ch == 6)  { MixerState::onSoloClicked(4);   return; }
        if (ch == 7)  { MixerState::onSelectClicked(4); return; }
        if (ch == 8)  { MixerState::onDynClicked(4);    return; }
        // C9~C15 预留备用通道（PCB 上不焊按键，直接忽略，不触发任何回调）
        // reserved for future expansion: add cases here if buttons 21~25 are ever populated
    }
}

// ──────────────────────────────────────────────────────────
// begin / update
// ──────────────────────────────────────────────────────────
void begin() {
    HC4067Scanner::onEvent(onHC4067Event);
}

void update() {
    // 实际处理在 HC4067Scanner::update() 触发的回调中完成
    // 此函数保留接口，便于将来添加轮询逻辑
}

} // namespace ButtonInput
