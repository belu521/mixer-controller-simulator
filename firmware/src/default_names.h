#pragma once
// firmware/src/default_names.h
// 默认通道名称表 — 与 mixer_simulator/core/controller.py _DEFAULT_CHANNEL_NAMES 完全一致
// Python 参考行: controller.py 第 20~28 行

#include <Arduino.h>

namespace DefaultNames {

// 32 个预设通道名称（索引 0 对应 CH1）
// 与 Python 模拟器 _DEFAULT_CHANNEL_NAMES 逐项一致
static const char* const TABLE[32] = {
    "Kick Drm",  // CH1
    "Snare",     // CH2
    "Hi-Hat",    // CH3
    "OHL",       // CH4
    "OHR",       // CH5
    "Tom 1",     // CH6
    "Tom 2",     // CH7
    "Tom 3",     // CH8
    "Bass Gtr",  // CH9
    "Elec Gtr",  // CH10
    "Acst Gtr",  // CH11
    "Piano",     // CH12
    "Keys",      // CH13
    "Synth",     // CH14
    "Pad",       // CH15
    "Strings",   // CH16
    "Brass 1",   // CH17
    "Brass 2",   // CH18
    "Sax",       // CH19
    "Flute",     // CH20
    "Vox Lead",  // CH21
    "Vox Bkg1",  // CH22
    "Vox Bkg2",  // CH23
    "Vox Harm",  // CH24
    "Choir",     // CH25
    "FX Revrb",  // CH26
    "FX Delay",  // CH27
    "FX Chor",   // CH28
    "Aux 1",     // CH29
    "Aux 2",     // CH30
    "Aux 3",     // CH31
    "Aux 4",     // CH32
};

// 固定长度缓冲区：用于 CH33~CH144 生成的名称（"CH33" 最长 6 字符）
static char _dynamicBuf[8];

/**
 * 根据通道号返回默认名称
 * @param chNum 通道号 1~144
 * @return 名称字符串指针（1~32 返回 TABLE，33~144 返回静态缓冲区）
 *
 * 对应 Python: _default_name(ch_num) — controller.py 第 31~35 行
 */
inline const char* get(int chNum) {
    if (chNum >= 1 && chNum <= 32) {
        return TABLE[chNum - 1];
    }
    // CH33~CH144: 动态生成 "CH{n}"（使用静态缓冲，非多线程安全，嵌入式单线程 OK）
    snprintf(_dynamicBuf, sizeof(_dynamicBuf), "CH%d", chNum);
    return _dynamicBuf;
}

} // namespace DefaultNames
