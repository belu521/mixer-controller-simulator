// firmware/src/mixer_state.cpp
// 混音台状态机实现 — 镜像 mixer_simulator/core/controller.py
// 对应 Python 行号已在关键处标注

#include "mixer_state.h"
#include "midi_io.h"
#include "default_names.h"
#include <string.h>

namespace MixerState {

// ──────────────────────────────────────────────────────────
// 全局状态存储（静态分配，Teensy 4.1 RAM 512KB 完全足够）
// ──────────────────────────────────────────────────────────
ChannelState channels[MAX_CHANNELS];
StripState   strips[NUM_STRIPS];

// ──────────────────────────────────────────────────────────
// 回调指针（默认 nullptr = 无操作）
// ──────────────────────────────────────────────────────────
static FaderCallback   _cbFaderChanged       = nullptr;
static ButtonCallback  _cbButtonChanged      = nullptr;
static EncoderCallback _cbEncoderValueChanged = nullptr;
static StripCallback   _cbEncoderModeChanged  = nullptr;
static StripCallback   _cbChannelSwitched     = nullptr;
static StripCallback   _cbPageTurnChanged     = nullptr;

// ──────────────────────────────────────────────────────────
// 默认起始通道（对应 Python _DEFAULT_CHANNELS = [1,8,15,23,32]）
// controller.py 第 90 行
// ──────────────────────────────────────────────────────────
static const uint8_t DEFAULT_CHANNELS[NUM_STRIPS] = { 1, 8, 15, 23, 32 };

// ──────────────────────────────────────────────────────────
// 内部辅助：初始化单个通道
// ──────────────────────────────────────────────────────────
static void initChannel(uint8_t idx) {
    ChannelState& ch = channels[idx];
    ch.chNum            = idx + 1;          // 通道号从 1 开始
    strncpy(ch.name, DefaultNames::get(ch.chNum), sizeof(ch.name) - 1);
    ch.name[sizeof(ch.name) - 1] = '\0';
    ch.faderValue       = 100;              // 默认推子值
    ch.muteActive       = false;
    ch.soloActive       = false;
    ch.selectActive     = false;
    ch.dynActive        = true;             // DYN 默认开启
    ch.compThr          = -20.0f;           // 压缩阈值默认 -20.0 dB
    ch.gateThr          = -40.0f;           // 门限阈值默认 -40.0 dB
    ch.pan              = 0;
    ch.encoderModeIndex = 0;                // 默认 COMP 模式
}

// ──────────────────────────────────────────────────────────
// begin() — 对应 Python __init__ — controller.py 第 94~108 行
// ──────────────────────────────────────────────────────────
void begin() {
    // 初始化 144 个通道
    for (uint8_t i = 0; i < MAX_CHANNELS; i++) {
        initChannel(i);
    }
    // 初始化 5 条推子条
    for (uint8_t i = 0; i < NUM_STRIPS; i++) {
        strips[i].stripId        = i;
        strips[i].currentChannel = DEFAULT_CHANNELS[i];
        strips[i].pageTurnMode   = false;
        strips[i].pageTurnTarget = DEFAULT_CHANNELS[i];
    }
}

// ──────────────────────────────────────────────────────────
// 状态获取
// ──────────────────────────────────────────────────────────
ChannelState& getChannel(uint8_t chNum) {
    // 保护越界访问
    if (chNum < 1 || chNum > MAX_CHANNELS) chNum = 1;
    return channels[chNum - 1];
}

StripState& getStrip(uint8_t stripId) {
    if (stripId >= NUM_STRIPS) stripId = 0;
    return strips[stripId];
}

ChannelState& getStripChannel(uint8_t stripId) {
    return getChannel(strips[stripId].currentChannel);
}

// ──────────────────────────────────────────────────────────
// onFaderMoved — 对应 Python on_fader_moved — controller.py 第 136~143 行
// ──────────────────────────────────────────────────────────
void onFaderMoved(uint8_t stripId, uint8_t value) {
    StripState&   strip = getStrip(stripId);
    ChannelState& ch    = getChannel(strip.currentChannel);
    ch.faderValue = value;
    // 发送 MIDI CC7（音量）
    MidiIO::sendCc(ch.chNum, CC_FADER, value);
    if (_cbFaderChanged) _cbFaderChanged(stripId, value);
}

// ──────────────────────────────────────────────────────────
// onEncoderRotated — 对应 Python on_encoder_rotated — controller.py 第 149~189 行
// ──────────────────────────────────────────────────────────
void onEncoderRotated(uint8_t stripId, int delta) {
    StripState& strip = getStrip(stripId);

    // 翻页模式：改变目标通道
    if (strip.pageTurnMode) {
        int newTarget = (int)strip.pageTurnTarget + delta;
        if (newTarget < 1) newTarget = 1;
        if (newTarget > MAX_CHANNELS) newTarget = MAX_CHANNELS;
        strip.pageTurnTarget = (uint8_t)newTarget;
        if (_cbPageTurnChanged) _cbPageTurnChanged(stripId);
        return;
    }

    // 正常模式：调整对应参数
    ChannelState& ch = getChannel(strip.currentChannel);
    char valStr[16];
    int  midiVal = 0;

    switch ((EncoderMode)ch.encoderModeIndex) {
        case EncoderMode::COMP: {
            // COMP 模式：调整压缩阈值，步进 0.5 dB
            // controller.py 第 166~170 行
            ch.compThr += delta * 0.5f;
            if (ch.compThr < -60.0f) ch.compThr = -60.0f;
            if (ch.compThr >   0.0f) ch.compThr =   0.0f;
            snprintf(valStr, sizeof(valStr), "%.1fdB", (double)ch.compThr);
            midiVal = (int)((ch.compThr + 60.0f) / 60.0f * 127.0f);
            if (midiVal < 0) midiVal = 0;
            if (midiVal > 127) midiVal = 127;
            MidiIO::sendCc(ch.chNum, CC_COMP_THR, (uint8_t)midiVal);
            break;
        }
        case EncoderMode::GATE: {
            // GATE 模式：调整门限阈值，步进 0.5 dB
            // controller.py 第 172~176 行
            ch.gateThr += delta * 0.5f;
            if (ch.gateThr < -80.0f) ch.gateThr = -80.0f;
            if (ch.gateThr >   0.0f) ch.gateThr =   0.0f;
            snprintf(valStr, sizeof(valStr), "%.1fdB", (double)ch.gateThr);
            midiVal = (int)((ch.gateThr + 80.0f) / 80.0f * 127.0f);
            if (midiVal < 0) midiVal = 0;
            if (midiVal > 127) midiVal = 127;
            MidiIO::sendCc(ch.chNum, CC_GATE_THR, (uint8_t)midiVal);
            break;
        }
        case EncoderMode::PAN:
        default: {
            // PAN 模式：整数步进 -63~63
            // controller.py 第 178~187 行
            int newPan = (int)ch.pan + delta;
            if (newPan < -63) newPan = -63;
            if (newPan >  63) newPan =  63;
            ch.pan = (int8_t)newPan;
            if (ch.pan < 0)
                snprintf(valStr, sizeof(valStr), "L%d", -ch.pan);
            else if (ch.pan > 0)
                snprintf(valStr, sizeof(valStr), "R%d", ch.pan);
            else
                strncpy(valStr, "C", sizeof(valStr));
            midiVal = ch.pan + 64;
            if (midiVal < 0) midiVal = 0;
            if (midiVal > 127) midiVal = 127;
            MidiIO::sendCc(ch.chNum, CC_PAN, (uint8_t)midiVal);
            break;
        }
    }

    if (_cbEncoderValueChanged) _cbEncoderValueChanged(stripId, valStr);
}

// ──────────────────────────────────────────────────────────
// onEncoderClicked — 对应 Python on_encoder_clicked — controller.py 第 191~206 行
// ──────────────────────────────────────────────────────────
void onEncoderClicked(uint8_t stripId) {
    StripState& strip = getStrip(stripId);

    if (strip.pageTurnMode) {
        // 翻页模式下：确认切换通道
        switchChannel(stripId, strip.pageTurnTarget);
        strip.pageTurnMode = false;
        if (_cbPageTurnChanged) _cbPageTurnChanged(stripId);
        return;
    }

    // 循环 COMP→GATE→PAN
    ChannelState& ch = getChannel(strip.currentChannel);
    ch.encoderModeIndex = (ch.encoderModeIndex + 1) % 3;
    if (_cbEncoderModeChanged) _cbEncoderModeChanged(stripId);
}

// ──────────────────────────────────────────────────────────
// onEncoderDoubleClicked — 对应 Python on_encoder_double_clicked
// controller.py 第 208~219 行
// ──────────────────────────────────────────────────────────
void onEncoderDoubleClicked(uint8_t stripId) {
    StripState& strip = getStrip(stripId);

    if (strip.pageTurnMode) {
        // 已在翻页模式 → 退出（取消）
        strip.pageTurnMode = false;
    } else {
        // 进入翻页模式
        strip.pageTurnMode   = true;
        strip.pageTurnTarget = strip.currentChannel;
    }
    if (_cbPageTurnChanged) _cbPageTurnChanged(stripId);
}

// ──────────────────────────────────────────────────────────
// onMuteClicked — controller.py 第 225~240 行
// ──────────────────────────────────────────────────────────
void onMuteClicked(uint8_t stripId) {
    ChannelState& ch = getStripChannel(stripId);
    ch.muteActive = !ch.muteActive;
    uint8_t note = (uint8_t)((NOTE_MUTE_BASE + ch.chNum - 1) % 128);
    if (ch.muteActive) MidiIO::sendNoteOn(ch.chNum, note);
    else               MidiIO::sendNoteOff(ch.chNum, note);
    if (_cbButtonChanged) _cbButtonChanged(stripId, "MUTE", ch.muteActive);
}

// ──────────────────────────────────────────────────────────
// onSoloClicked — controller.py 第 242~251 行
// ──────────────────────────────────────────────────────────
void onSoloClicked(uint8_t stripId) {
    ChannelState& ch = getStripChannel(stripId);
    ch.soloActive = !ch.soloActive;
    uint8_t note = (uint8_t)((NOTE_SOLO_BASE + ch.chNum - 1) % 128);
    if (ch.soloActive) MidiIO::sendNoteOn(ch.chNum, note);
    else               MidiIO::sendNoteOff(ch.chNum, note);
    if (_cbButtonChanged) _cbButtonChanged(stripId, "SOLO", ch.soloActive);
}

// ──────────────────────────────────────────────────────────
// onSelectClicked — SELECT 互斥 — controller.py 第 253~270 行
// ──────────────────────────────────────────────────────────
void onSelectClicked(uint8_t stripId) {
    // 先清除其他所有条的 SELECT 状态（互斥）
    uint8_t targetCh = strips[stripId].currentChannel;
    for (uint8_t i = 0; i < NUM_STRIPS; i++) {
        ChannelState& other = getChannel(strips[i].currentChannel);
        if (i != stripId && other.selectActive) {
            other.selectActive = false;
            if (_cbButtonChanged) _cbButtonChanged(i, "SELECT", false);
        }
    }
    // 切换本条 SELECT
    ChannelState& ch = getChannel(targetCh);
    ch.selectActive = !ch.selectActive;
    uint8_t note = (uint8_t)((NOTE_SELECT_BASE + ch.chNum - 1) % 128);
    if (ch.selectActive) MidiIO::sendNoteOn(ch.chNum, note);
    else                 MidiIO::sendNoteOff(ch.chNum, note);
    if (_cbButtonChanged) _cbButtonChanged(stripId, "SELECT", ch.selectActive);
}

// ──────────────────────────────────────────────────────────
// onDynClicked — controller.py 第 272~281 行
// ──────────────────────────────────────────────────────────
void onDynClicked(uint8_t stripId) {
    ChannelState& ch = getStripChannel(stripId);
    ch.dynActive = !ch.dynActive;
    uint8_t note = (uint8_t)((NOTE_DYN_BASE + ch.chNum - 1) % 128);
    if (ch.dynActive) MidiIO::sendNoteOn(ch.chNum, note);
    else              MidiIO::sendNoteOff(ch.chNum, note);
    if (_cbButtonChanged) _cbButtonChanged(stripId, "DYN", ch.dynActive);
}

// ──────────────────────────────────────────────────────────
// switchChannel — controller.py 第 291~299 行
// ──────────────────────────────────────────────────────────
void switchChannel(uint8_t stripId, uint8_t newCh) {
    StripState& strip = getStrip(stripId);
    if (strip.currentChannel == newCh) return;
    strip.currentChannel = newCh;
    if (_cbChannelSwitched) _cbChannelSwitched(stripId);
}

// ──────────────────────────────────────────────────────────
// 回调注册
// ──────────────────────────────────────────────────────────
void onFaderChanged(FaderCallback cb)           { _cbFaderChanged = cb; }
void onButtonChanged(ButtonCallback cb)         { _cbButtonChanged = cb; }
void onEncoderValueChanged(EncoderCallback cb)  { _cbEncoderValueChanged = cb; }
void onEncoderModeChanged(StripCallback cb)     { _cbEncoderModeChanged = cb; }
void onChannelSwitched(StripCallback cb)        { _cbChannelSwitched = cb; }
void onPageTurnModeChanged(StripCallback cb)    { _cbPageTurnChanged = cb; }

} // namespace MixerState
