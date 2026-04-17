# firmware/HARDWARE.md

# 完整接线表（Teensy 4.1 混音台控制器）

> ⚠️ 本文档与仓库原有 `docs_pinout_Version1.md` 内容一致（电机供电已更新为 10V，MTR2 IN1/IN2 已按最终接线图确认）。**不修改原文档**。

---

## 1. 电源树

| 输入 | 转换器 | 输出 | 用途 |
|---|---|---|---|
| 12V DC 输入 | 开关 | +12V_SW | 主电源 |
| +12V_SW | MP2315 #1 | +5V_LED (5V) | WS2812B VCC + AMS1117 输入 |
| +5V_LED | AMS1117-3.3 | +3V3_LOGIC (3.3V) | MCU / OLED / TCA9548A / HC4067 VCC / TB6612 VCC |
| +12V_SW | MP2315 #2 | +10V_MOTOR (10V) | TB6612 VM（电机驱动电源）|

---

## 2. MCU — Teensy 4.1

- 供电：由 AMS1117-3.3 提供 3.3V（VIN 引脚 or 3.3V 引脚）
- USB：连接 PC 作为 USB MIDI + 串口调试设备

---

## 3. 推子 ADC × 5

电位器供电：Pin1=GND，Pin3=3.3V，Pin2(Wiper)→Teensy ADC

| 推子 | ADC 引脚 | Arduino 模拟通道 |
|---|---|---|
| Fader1 | **Pin14** | A0 |
| Fader2 | **Pin15** | A1 |
| Fader3 | **Pin16** | A2 |
| Fader4 | **Pin17** | A3 |
| Fader5 | **Pin20** | A6 |

---

## 4. 电机控制 × 5（TB6612FNG × 3）

**VM = +10V_MOTOR**，**STBY = VCC = +3V3_LOGIC**

### TB6612FNG_1（驱动 Fader1 + Fader2）

| 信号 | Teensy 引脚 | TB6612 脚 | 说明 |
|---|---|---|---|
| MTR1_PWM | Pin23 | PWMA | Fader1 速度 |
| MTR1_IN1 | Pin41 | AIN1 | Fader1 方向 |
| MTR1_IN2 | Pin40 | AIN2 | Fader1 方向 |
| MTR2_PWM | Pin22 | PWMB | Fader2 速度 |
| **MTR2_IN1** | **Pin38** | BIN1 | Fader2 方向（已按最终接线图确认）|
| **MTR2_IN2** | **Pin39** | BIN2 | Fader2 方向（已按最终接线图确认）|

输出：`AO1/AO2` → Fader1 电机；`BO1/BO2` → Fader2 电机

### TB6612FNG_2（驱动 Fader3 + Fader4）

| 信号 | Teensy 引脚 | TB6612 脚 |
|---|---|---|
| MTR3_PWM | Pin21 | PWMA |
| MTR3_IN1 | Pin37 | AIN1 |
| MTR3_IN2 | Pin36 | AIN2 |
| MTR4_PWM | Pin13 | PWMB |
| MTR4_IN1 | Pin35 | BIN1 |
| MTR4_IN2 | Pin34 | BIN2 |

### TB6612FNG_3（驱动 Fader5，B 通道空置）

| 信号 | Teensy 引脚 | TB6612 脚 |
|---|---|---|
| MTR5_PWM | Pin31 | PWMA |
| MTR5_IN1 | Pin32 | AIN1 |
| MTR5_IN2 | Pin33 | AIN2 |

### TB6612 H 桥真值表

| IN1 | IN2 | PWM | 动作 |
|---|---|---|---|
| 1 | 0 | duty | 正转（推子向上）|
| 0 | 1 | duty | 反转（推子向下）|
| 1 | 1 | × | 刹车（短路制动）|
| 0 | 0 | 0 | 滑行（断开）|

---

## 5. 编码器 × 5（EC11）

硬件去抖：每路 A/B 各接 100nF → GND + 10kΩ → 3.3V 上拉

| 编码器 | A 相引脚 | B 相引脚 | 按键 → |
|---|---|---|---|
| ENC1 | Pin0 | Pin1 | HC4067_1 C0 |
| ENC2 | Pin2 | Pin3 | HC4067_1 C1 |
| ENC3 | Pin4 | Pin5 | HC4067_1 C2 |
| ENC4 | Pin6 | Pin7 | HC4067_1 C3 |
| ENC5 | Pin8 | Pin9 | HC4067_1 C4 |

---

## 6. HC4067 × 3（16 路多路复用器）

**共享选择脚**：S0=Pin26，S1=Pin27，S2=Pin28，S3=Pin29  
**EN = GND（常开）**，**VCC = 3.3V**

### HC4067_1（SIG = Pin11）

| 通道 | 接线目标 | 功能 |
|---|---|---|
| C0 | ENC1 按键 | Encoder1 单击/双击 |
| C1 | ENC2 按键 | Encoder2 单击/双击 |
| C2 | ENC3 按键 | Encoder3 单击/双击 |
| C3 | ENC4 按键 | Encoder4 单击/双击 |
| C4 | ENC5 按键 | Encoder5 单击/双击 |
| C5 | 按键1 | Strip1 MUTE |
| C6 | 按键2 | Strip1 SOLO |
| C7 | 按键3 | Strip1 SELECT |
| C8 | 按键4 | Strip1 DYN |
| C9 | 按键5 | Strip2 MUTE |
| C10 | 按键6 | Strip2 SOLO |
| C11 | 按键7 | Strip2 SELECT |
| C12 | 按键8 | Strip2 DYN |
| C13 | 按键9 | Strip3 MUTE |
| C14 | 按键10 | Strip3 SOLO |
| C15 | 按键11 | Strip3 SELECT |

### HC4067_2（SIG = Pin12）

| 通道 | 接线目标 | 功能 |
|---|---|---|
| C0 | 按键12 | Strip3 DYN |
| C1 | 按键13 | Strip4 MUTE |
| C2 | 按键14 | Strip4 SOLO |
| C3 | 按键15 | Strip4 SELECT |
| C4 | 按键16 | Strip4 DYN |
| C5 | 按键17 | Strip5 MUTE |
| C6 | 按键18 | Strip5 SOLO |
| C7 | 按键19 | Strip5 SELECT |
| C8 | 按键20 | Strip5 DYN |
| C9~C15 | 空置 | — |

### HC4067_3（SIG = Pin24）

| 通道 | 状态 |
|---|---|
| C0~C15 | 全部备用（将来扩展用，固件已扫描并预留回调钩子）|

---

## 7. OLED × 5（SSD1306 128×64）

- I2C 总线：**Pin18 = SDA**，**Pin19 = SCL**（4.7kΩ 上拉至 3.3V）
- TCA9548A 地址：**0x70**（A0/A1/A2 全接 GND）
- OLED 地址：**0x3C**（所有 OLED 相同，由 TCA9548A 分通道访问）

| TCA9548A 通道 | OLED | 对应 Strip |
|---|---|---|
| 0 | OLED1 | Strip1 |
| 1 | OLED2 | Strip2 |
| 2 | OLED3 | Strip3 |
| 3 | OLED4 | Strip4 |
| 4 | OLED5 | Strip5 |

---

## 8. WS2812B LED × 25

- 数据线：**Pin10** → 330Ω 串联电阻 → LED1 DIN
- VCC：**+5V_LED（5V）**
- GND：与 Teensy 共地
- 串联数量：25 颗（Strip1~5 各 5 颗）

---

## 9. 引脚速查表

| Teensy 引脚 | 功能 | 方向 |
|---|---|---|
| 0 | ENC1_A | IN |
| 1 | ENC1_B | IN |
| 2 | ENC2_A | IN |
| 3 | ENC2_B | IN |
| 4 | ENC3_A | IN |
| 5 | ENC3_B | IN |
| 6 | ENC4_A | IN |
| 7 | ENC4_B | IN |
| 8 | ENC5_A | IN |
| 9 | ENC5_B | IN |
| 10 | WS2812B DATA | OUT |
| 11 | HC4067_1 SIG | IN |
| 12 | HC4067_2 SIG | IN |
| 13 | MTR4_PWM | OUT |
| 14 (A0) | FADER1_ADC | IN |
| 15 (A1) | FADER2_ADC | IN |
| 16 (A2) | FADER3_ADC | IN |
| 17 (A3) | FADER4_ADC | IN |
| 18 | I2C_SDA | I2C |
| 19 | I2C_SCL | I2C |
| 20 (A6) | FADER5_ADC | IN |
| 21 | MTR3_PWM | OUT |
| 22 | MTR2_PWM | OUT |
| 23 | MTR1_PWM | OUT |
| 24 | HC4067_3 SIG | IN |
| 26 | HC4067_S0 | OUT |
| 27 | HC4067_S1 | OUT |
| 28 | HC4067_S2 | OUT |
| 29 | HC4067_S3 | OUT |
| 31 | MTR5_PWM | OUT |
| 32 | MTR5_IN1 | OUT |
| 33 | MTR5_IN2 | OUT |
| 34 | MTR4_IN2 | OUT |
| 35 | MTR4_IN1 | OUT |
| 36 | MTR3_IN2 | OUT |
| 37 | MTR3_IN1 | OUT |
| 38 | MTR2_IN1 | OUT |
| 39 | MTR2_IN2 | OUT |
| 40 | MTR1_IN2 | OUT |
| 41 | MTR1_IN1 | OUT |
