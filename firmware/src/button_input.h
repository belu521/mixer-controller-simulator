#pragma once
// firmware/src/button_input.h
// 按键输入映射头文件
// 将 HC4067 扫描事件映射为高层 MixerState 操作

#include <Arduino.h>

namespace ButtonInput {

// 初始化（注册 HC4067Scanner 事件回调）
void begin();

// 更新（空函数，实际处理在 HC4067Scanner 回调中完成）
void update();

} // namespace ButtonInput
