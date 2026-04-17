// firmware/src/midi_io.cpp
// USB MIDI 收发实现 — 对应 Python mixer_simulator/midi/midi_engine.py
// 以及 controller.py 第 301~327 行的 _send_* 方法

#include "midi_io.h"

namespace MidiIO {

// ──────────────────────────────────────────────────────────
// 接收回调指针
// ──────────────────────────────────────────────────────────
static CcCallback   _cbCc      = nullptr;
static NoteCallback _cbNoteOn  = nullptr;
static NoteCallback _cbNoteOff = nullptr;

// ──────────────────────────────────────────────────────────
// begin() — 初始化 USB MIDI
// Teensy 内置 USB MIDI 无需额外初始化，只需确保编译时
// 选择了 USB_MIDI_SERIAL (platformio.ini build_flags)
// ──────────────────────────────────────────────────────────
void begin() {
    // usbMIDI 是 Teensy 内置全局对象，无需 begin()
    // 串口调试
    Serial.println("[MidiIO] USB MIDI ready");
}

// ──────────────────────────────────────────────────────────
// sendCc — controller.py 第 305~311 行
// ──────────────────────────────────────────────────────────
void sendCc(uint8_t chNum, uint8_t cc, uint8_t value) {
    uint8_t midiCh = midiChannelOf(chNum);
    usbMIDI.sendControlChange(cc, value, midiCh);
    // 刷新 USB 缓冲（Teensy 要求）
    usbMIDI.send_now();
}

// ──────────────────────────────────────────────────────────
// sendNoteOn — controller.py 第 313~319 行（velocity=127）
// ──────────────────────────────────────────────────────────
void sendNoteOn(uint8_t chNum, uint8_t note) {
    uint8_t midiCh = midiChannelOf(chNum);
    usbMIDI.sendNoteOn(note, 127, midiCh);
    usbMIDI.send_now();
}

// ──────────────────────────────────────────────────────────
// sendNoteOff — controller.py 第 321~327 行（velocity=0）
// ──────────────────────────────────────────────────────────
void sendNoteOff(uint8_t chNum, uint8_t note) {
    uint8_t midiCh = midiChannelOf(chNum);
    usbMIDI.sendNoteOff(note, 0, midiCh);
    usbMIDI.send_now();
}

// ──────────────────────────────────────────────────────────
// update() — 处理接收到的 MIDI 消息（在 loop() 中调用）
// ──────────────────────────────────────────────────────────
void update() {
    while (usbMIDI.read()) {
        uint8_t type = usbMIDI.getType();
        uint8_t ch   = usbMIDI.getChannel();
        uint8_t d1   = usbMIDI.getData1();
        uint8_t d2   = usbMIDI.getData2();

        switch (type) {
            case usbMIDI.ControlChange:
                if (_cbCc) _cbCc(ch, d1, d2);
                break;
            case usbMIDI.NoteOn:
                if (d2 > 0) {
                    if (_cbNoteOn) _cbNoteOn(ch, d1, d2);
                } else {
                    // velocity=0 视为 NoteOff
                    if (_cbNoteOff) _cbNoteOff(ch, d1, 0);
                }
                break;
            case usbMIDI.NoteOff:
                if (_cbNoteOff) _cbNoteOff(ch, d1, d2);
                break;
            default:
                break;
        }
    }
}

// ──────────────────────────────────────────────────────────
// 回调注册
// ──────────────────────────────────────────────────────────
void onCcReceived(CcCallback cb)       { _cbCc = cb; }
void onNoteOnReceived(NoteCallback cb) { _cbNoteOn = cb; }
void onNoteOffReceived(NoteCallback cb){ _cbNoteOff = cb; }

} // namespace MidiIO
