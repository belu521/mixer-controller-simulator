#pragma once
// firmware/src/mixer_state.h
// 混音台状态机头文件 — 镜像 mixer_simulator/core/controller.py
// 包含: ChannelState / StripState / MixerState 命名空间

#include <Arduino.h>

// ──────────────────────────────────────────────────────────
// MIDI 映射常量（与 controller.py 完全一致）
// Python 参考: controller.py 第 8~17 行
// ──────────────────────────────────────────────────────────
constexpr uint8_t CC_FADER     = 7;    // 推子音量
constexpr uint8_t CC_COMP_THR  = 18;   // 压缩阈值
constexpr uint8_t CC_GATE_THR  = 16;   // 门限阈值
constexpr uint8_t CC_PAN       = 10;   // 声像

constexpr uint8_t NOTE_MUTE_BASE   = 0;   // MUTE Note 基址
constexpr uint8_t NOTE_SOLO_BASE   = 32;  // SOLO Note 基址
constexpr uint8_t NOTE_SELECT_BASE = 64;  // SELECT Note 基址
constexpr uint8_t NOTE_DYN_BASE    = 96;  // DYN Note 基址

// 编码器模式枚举（与 ENCODER_MODES 列表对应）
enum class EncoderMode : uint8_t {
    COMP = 0,
    GATE = 1,
    PAN  = 2,
};

constexpr uint8_t MAX_CHANNELS = 144;
constexpr uint8_t NUM_STRIPS   = 5;

// ──────────────────────────────────────────────────────────
// ChannelState — 单个通道的完整状态
// 对应 Python: class ChannelState — controller.py 第 38~52 行
// ──────────────────────────────────────────────────────────
struct ChannelState {
    uint8_t  chNum;               // 通道号 1~144
    char     name[12];            // 通道名（固定长度缓冲）
    uint8_t  faderValue;          // 推子值 0~127，默认 100
    bool     muteActive;          // 静音，默认 false
    bool     soloActive;          // 独奏，默认 false
    bool     selectActive;        // 选中，默认 false
    bool     dynActive;           // 动态处理，默认 true
    float    compThr;             // 压缩阈值 -60~0 dB，默认 -20.0
    float    gateThr;             // 门限阈值 -80~0 dB，默认 -40.0
    int8_t   pan;                 // 声像 -63~63，默认 0
    uint8_t  encoderModeIndex;    // 编码器模式 0=COMP,1=GATE,2=PAN，默认 0
};

// ──────────────────────────────────────────────────────────
// StripState — 单个物理推子条状态
// 对应 Python: class StripState — controller.py 第 55~62 行
// ──────────────────────────────────────────────────────────
struct StripState {
    uint8_t stripId;           // 物理条编号 0~4
    uint8_t currentChannel;    // 当前映射通道号 1~144
    bool    pageTurnMode;      // 是否在翻页模式
    uint8_t pageTurnTarget;    // 翻页模式中选中的目标通道（1~144，但实际存储为 uint8_t 限制 255，通道最多 144 OK）
};

// ──────────────────────────────────────────────────────────
// 回调函数类型（用于向上层通知状态变化）
// ──────────────────────────────────────────────────────────
using StripCallback   = void (*)(uint8_t stripId);
using ButtonCallback  = void (*)(uint8_t stripId, const char* btn, bool active);
using FaderCallback   = void (*)(uint8_t stripId, uint8_t value);
using EncoderCallback = void (*)(uint8_t stripId, const char* valueStr);

namespace MixerState {

// 状态存储（全局，无动态内存）
extern ChannelState channels[MAX_CHANNELS];  // 索引 0 = CH1
extern StripState   strips[NUM_STRIPS];

// 初始化（复刻 Python __init__）
void begin();

// ──── 获取状态 ────
ChannelState& getChannel(uint8_t chNum);           // chNum 1~144
StripState&   getStrip(uint8_t stripId);           // stripId 0~4
ChannelState& getStripChannel(uint8_t stripId);    // 获取 strip 当前通道的状态

// ──── 推子操作 ────
// 对应 Python: on_fader_moved — controller.py 第 136~143 行
void onFaderMoved(uint8_t stripId, uint8_t value);

// ──── 编码器操作 ────
// 对应 Python: on_encoder_rotated — controller.py 第 149~189 行
void onEncoderRotated(uint8_t stripId, int delta);

// 对应 Python: on_encoder_clicked — controller.py 第 191~206 行
void onEncoderClicked(uint8_t stripId);

// 对应 Python: on_encoder_double_clicked — controller.py 第 208~219 行
void onEncoderDoubleClicked(uint8_t stripId);

// ──── 按键操作 ────
// 对应 Python: on_mute_clicked — controller.py 第 225~240 行
void onMuteClicked(uint8_t stripId);

// 对应 Python: on_solo_clicked — controller.py 第 242~251 行
void onSoloClicked(uint8_t stripId);

// 对应 Python: on_select_clicked — controller.py 第 253~270 行（SELECT 互斥）
void onSelectClicked(uint8_t stripId);

// 对应 Python: on_dyn_clicked — controller.py 第 272~281 行
void onDynClicked(uint8_t stripId);

// ──── 通道切换（内部 + 外部可调用）────
// 对应 Python: _switch_channel — controller.py 第 291~299 行
void switchChannel(uint8_t stripId, uint8_t newCh);

// ──── 回调注册 ────
void onFaderChanged(FaderCallback cb);
void onButtonChanged(ButtonCallback cb);
void onEncoderValueChanged(EncoderCallback cb);
void onEncoderModeChanged(StripCallback cb);
void onChannelSwitched(StripCallback cb);
void onPageTurnModeChanged(StripCallback cb);

} // namespace MixerState
