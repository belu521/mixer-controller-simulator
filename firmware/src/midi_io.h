#pragma once
// firmware/src/midi_io.h
// USB MIDI 收发接口 — 镜像 mixer_simulator/core/controller.py 中的 MIDI 方法
// 对应 Python: _send_cc / _send_note_on / _send_note_off / _midi_channel
// controller.py 第 301~327 行

#include <Arduino.h>

namespace MidiIO {

// 初始化 USB MIDI
void begin();

/**
 * 计算 MIDI 通道号（1~16 循环）
 * 对应 Python: _midi_channel(ch_num) = (ch_num - 1) % 16 + 1
 * controller.py 第 301~303 行
 */
inline uint8_t midiChannelOf(uint8_t chNum) {
    return (chNum - 1) % 16 + 1;
}

/**
 * 发送 MIDI CC 消息
 * 对应 Python: _send_cc — controller.py 第 305~311 行
 * @param chNum   源通道号（1~144），用于计算 MIDI 通道
 * @param cc      CC 编号
 * @param value   CC 值（0~127，调用方保证已限幅）
 */
void sendCc(uint8_t chNum, uint8_t cc, uint8_t value);

/**
 * 发送 MIDI Note On（velocity=127）
 * 对应 Python: _send_note_on — controller.py 第 313~319 行
 */
void sendNoteOn(uint8_t chNum, uint8_t note);

/**
 * 发送 MIDI Note Off（velocity=0）
 * 对应 Python: _send_note_off — controller.py 第 321~327 行
 */
void sendNoteOff(uint8_t chNum, uint8_t note);

/**
 * 处理接收到的 MIDI 消息（远端反向控制电动推子/OLED）
 * 在 loop() 中周期调用
 */
void update();

// 接收回调注册：收到 CC7 时通知 FaderDriver 移动到目标位置
using CcCallback   = void (*)(uint8_t midiCh, uint8_t cc, uint8_t value);
using NoteCallback = void (*)(uint8_t midiCh, uint8_t note, uint8_t velocity);

void onCcReceived(CcCallback cb);
void onNoteOnReceived(NoteCallback cb);
void onNoteOffReceived(NoteCallback cb);

} // namespace MidiIO
