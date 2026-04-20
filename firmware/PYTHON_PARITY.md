# firmware/PYTHON_PARITY.md

# Python 模拟器 ↔ MCU 固件行为对照表

> **硬件变更说明（最终版）**：HC4067_3 已从最终硬件移除（不焊接）。固件代码中 `NUM_HC4067 = 2`，HC4067_3 的扫描循环和事件分发已清理。接口设计保留了对将来扩展第 3 片的兼容性（通过 `constexpr NUM_HC4067` 控制，修改一处即可启用）。**此变更对 Python 模拟器行为无影响**：Python 模拟器层面本来就没有 HC4067 概念，所有按键均通过 GUI 按钮触发。

本文档逐项对比 Python 模拟器（`mixer_simulator/`）与 Teensy 4.1 固件（`firmware/src/`）的行为，确保两者完全一致。

---

## 1. 常量对照

| Python 模拟器 | 位置 | 固件 | 位置 | 值 | 说明 |
|---|---|---|---|---|---|
| `CC_FADER` | controller.py:9 | `CC_FADER` | mixer_state.h:15 | `7` | 推子音量 CC 编号 |
| `CC_COMP_THR` | controller.py:10 | `CC_COMP_THR` | mixer_state.h:16 | `18` | 压缩阈值 CC 编号 |
| `CC_GATE_THR` | controller.py:11 | `CC_GATE_THR` | mixer_state.h:17 | `16` | 门限阈值 CC 编号 |
| `CC_PAN` | controller.py:12 | `CC_PAN` | mixer_state.h:18 | `10` | 声像 CC 编号 |
| `NOTE_MUTE_BASE` | controller.py:14 | `NOTE_MUTE_BASE` | mixer_state.h:20 | `0` | MUTE Note 基址 |
| `NOTE_SOLO_BASE` | controller.py:15 | `NOTE_SOLO_BASE` | mixer_state.h:21 | `32` | SOLO Note 基址 |
| `NOTE_SELECT_BASE` | controller.py:16 | `NOTE_SELECT_BASE` | mixer_state.h:22 | `64` | SELECT Note 基址 |
| `NOTE_DYN_BASE` | controller.py:17 | `NOTE_DYN_BASE` | mixer_state.h:23 | `96` | DYN Note 基址 |
| `MixerController.MAX_CHANNELS` | controller.py:92 | `MAX_CHANNELS` | mixer_state.h:29 | `144` | 最大通道数 |
| `MixerController._DEFAULT_CHANNELS` | controller.py:90 | `DEFAULT_CHANNELS[]` | mixer_state.cpp:34 | `[1,8,15,23,32]` | Strip 默认起始通道 |
| `ENCODER_MODES` | controller.py:66 | `EncoderMode` enum | mixer_state.h:27 | `COMP=0,GATE=1,PAN=2` | 编码器模式 |

---

## 2. 默认通道名称

| Python 模拟器 | 位置 | 固件 | 位置 | 说明 |
|---|---|---|---|---|
| `_DEFAULT_CHANNEL_NAMES` (32项) | controller.py:20~28 | `DefaultNames::TABLE[]` (32项) | default_names.h:16~47 | 逐项完全一致 |
| `_default_name(ch_num)` | controller.py:31~35 | `DefaultNames::get(chNum)` | default_names.h:55~64 | 1~32返回表中名，33~144返回 "CH{n}" |

---

## 3. 状态结构对照

### ChannelState

| Python 字段 | controller.py 行 | 固件字段 | 类型 | 默认值 |
|---|---|---|---|---|
| `ch_num` | 42 | `chNum` | `uint8_t` | — |
| `channel_name` | 43 | `name[12]` | `char[]` | `DefaultNames::get(chNum)` |
| `fader_value` | 44 | `faderValue` | `uint8_t` | `100` |
| `mute_active` | 45 | `muteActive` | `bool` | `false` |
| `solo_active` | 46 | `soloActive` | `bool` | `false` |
| `select_active` | 47 | `selectActive` | `bool` | `false` |
| `dyn_active` | 48 | `dynActive` | `bool` | `true` |
| `comp_thr` | 49 | `compThr` | `float` | `-20.0f` |
| `gate_thr` | 50 | `gateThr` | `float` | `-40.0f` |
| `pan` | 51 | `pan` | `int8_t` | `0` |
| `encoder_mode_index` | 52 | `encoderModeIndex` | `uint8_t` | `0` |

### StripState

| Python 字段 | controller.py 行 | 固件字段 | 类型 |
|---|---|---|---|
| `strip_id` | 59 | `stripId` | `uint8_t` |
| `current_channel` | 60 | `currentChannel` | `uint8_t` |
| `page_turn_mode` | 61 | `pageTurnMode` | `bool` |
| `page_turn_target` | 62 | `pageTurnTarget` | `uint8_t` |

---

## 4. 方法对照

| Python 方法 | controller.py 行 | 固件方法 | 固件位置 | 说明 |
|---|---|---|---|---|
| `on_fader_moved(strip_id, value)` | 136~143 | `MixerState::onFaderMoved(stripId, value)` | mixer_state.cpp | 更新 faderValue，发送 CC7 |
| `on_encoder_rotated(strip_id, delta)` | 149~189 | `MixerState::onEncoderRotated(stripId, delta)` | mixer_state.cpp | 翻页/COMP/GATE/PAN 调整 |
| `on_encoder_clicked(strip_id)` | 191~206 | `MixerState::onEncoderClicked(stripId)` | mixer_state.cpp | 翻页确认 or 循环模式 |
| `on_encoder_double_clicked(strip_id)` | 208~219 | `MixerState::onEncoderDoubleClicked(stripId)` | mixer_state.cpp | 进入/退出翻页模式 |
| `on_mute_clicked(strip_id)` | 225~240 | `MixerState::onMuteClicked(stripId)` | mixer_state.cpp | 切换 MUTE，发 NoteOn/Off |
| `on_solo_clicked(strip_id)` | 242~251 | `MixerState::onSoloClicked(stripId)` | mixer_state.cpp | 切换 SOLO，发 NoteOn/Off |
| `on_select_clicked(strip_id)` | 253~270 | `MixerState::onSelectClicked(stripId)` | mixer_state.cpp | SELECT 互斥 + NoteOn/Off |
| `on_dyn_clicked(strip_id)` | 272~281 | `MixerState::onDynClicked(stripId)` | mixer_state.cpp | 切换 DYN，发 NoteOn/Off |
| `_switch_channel(strip_id, new_ch)` | 291~299 | `MixerState::switchChannel(stripId, newCh)` | mixer_state.cpp | 更新 currentChannel |
| `_midi_channel(ch_num)` | 301~303 | `MidiIO::midiChannelOf(chNum)` | midi_io.h | `(chNum-1) % 16 + 1` |
| `_send_cc(ch_num, cc, value)` | 305~311 | `MidiIO::sendCc(chNum, cc, value)` | midi_io.cpp | 发送 MIDI CC |
| `_send_note_on(ch_num, note)` | 313~319 | `MidiIO::sendNoteOn(chNum, note)` | midi_io.cpp | 发送 NoteOn（vel=127）|
| `_send_note_off(ch_num, note)` | 321~327 | `MidiIO::sendNoteOff(chNum, note)` | midi_io.cpp | 发送 NoteOff（vel=0）|

---

## 5. MIDI 映射公式对照

| 功能 | Python 公式 | 固件公式 | 位置 |
|---|---|---|---|
| MIDI 通道计算 | `(ch_num - 1) % 16 + 1` | `(chNum - 1) % 16 + 1` | midi_io.h |
| Note 计算 | `(BASE + ch_num - 1) % 128` | `(BASE + chNum - 1) % 128` | mixer_state.cpp |
| COMP MIDI 值 | `int((comp_thr + 60) / 60 * 127)` | `(compThr + 60.0f) / 60.0f * 127.0f` | mixer_state.cpp |
| GATE MIDI 值 | `int((gate_thr + 80) / 80 * 127)` | `(gateThr + 80.0f) / 80.0f * 127.0f` | mixer_state.cpp |
| PAN MIDI 值 | `pan + 64` | `pan + 64` | mixer_state.cpp |
| COMP 步进 | `delta * 0.5` | `delta * 0.5f` | mixer_state.cpp |
| GATE 步进 | `delta * 0.5` | `delta * 0.5f` | mixer_state.cpp |

---

## 6. dB 转换对照

| Python | 位置 | 固件 | 位置 | 公式 |
|---|---|---|---|---|
| `midi_to_db(midi_val)` | fader_widget.py:20~26 | `midiToDb(midi, buf, bufLen)` | oled_display.cpp | `db = (midi - 100) * 0.5`；`midi=0` → `"-inf dB"` |

---

## 7. SELECT 互斥逻辑对照

| Python | controller.py 行 | 固件 | mixer_state.cpp |
|---|---|---|---|
| `for i, strip in enumerate(self._strips):` 先清除其他 SELECT | 256~261 | `for (uint8_t i = 0; i < NUM_STRIPS; i++)` 先清除其他 SELECT | onSelectClicked |
| 再切换本条 SELECT（toggle） | 263~270 | 再切换本条 SELECT（toggle） | onSelectClicked |

---

## 8. 翻页模式逻辑对照

| 行为 | Python | 固件 |
|---|---|---|
| 双击进入 | `on_encoder_double_clicked` → `page_turn_mode = True` | `onEncoderDoubleClicked` → `pageTurnMode = true` |
| 双击退出 | `on_encoder_double_clicked` → `page_turn_mode = False` | `onEncoderDoubleClicked` → `pageTurnMode = false` |
| 旋转选通道 | `on_encoder_rotated` 中 `if strip.page_turn_mode:` | `onEncoderRotated` 中 `if (strip.pageTurnMode)` |
| 单击确认 | `on_encoder_clicked` → `_switch_channel` | `onEncoderClicked` → `switchChannel` |
| OLED 渲染 | UI `page_turn_mode_changed` 信号 → 翻页界面 | `renderChannelBank(stripId, pageTurnTarget)` |

---

## 9. 编码器加速对照

| Python | 固件 |
|---|---|
| `delta` 传入已含 GUI 加速（PyQt 滚轮速度自适应） | `encoder_input.cpp` 中：步进间隔 < `ACCEL_FAST_MS`(80ms) → `delta × ACCEL_MULT`(4) |

---

## 10. 新增硬件功能（Python 模拟器无对应）

| 功能 | 固件模块 | 说明 |
|---|---|---|
| ADC 采样 + IIR 滤波 | `fader_driver.cpp` | 硬件推子 → MIDI 值（Python 模拟器用虚拟滑块代替）|
| 电机闭环控制 | `fader_driver.cpp` | 电动推子自动移动到目标位置 |
| 用户接触检测 | `fader_driver.cpp` | 检测用户手动推动，停止电机避免对抗 |
| HC4067 扫描 | `hc4067_scanner.cpp` | 物理按键扫描（Python 用 GUI 按钮代替）|
| WS2812B LED | `led_feedback.cpp` | 状态 LED 反馈（Python 用颜色指示代替）|
