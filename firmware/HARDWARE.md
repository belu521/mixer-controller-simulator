# firmware/HARDWARE.md

# 硬件参考手册（最终版）

> 本文档是硬件权威参考，对应底层 + 上层 PCB 原理图最终审查结果。  
> 如与旧版 `docs_pinout_Version1.md` 有冲突，以本文档为准。

---

## 3.1 总览

### 双层 PCB 设计

| 层 | 内容 |
|---|---|
| **底层 PCB** | MCU（Teensy 4.1）、电源（MP2315/AMS1117/外部降压）、HC4067 × 2、TB6612 × 3 |
| **上层 PCB** | OLED × 5、EC11 编码器 × 5、推子条按键 × 20、WS2812B LED × 25 |

### 层间连接排针

| 排针 | 底层 | 上层 | 内容 |
|---|---|---|---|
| U7 / U38 | U7（底层） | U38（上层） | OLED SDA/SCL、编码器 A/B × 5、WS2812 数据、5V/3.3V/GND（16pin） |
| U3 / U27 | U3（底层 HC4067_1 控制） | U27（上层 HC4067_1 通道） | HC4067_1 SIG/S0~S3/EN/VCC/GND（8pin）+ 16 通道（16pin） |
| U5 / U28 | U5（底层 HC4067_2 控制） | U28（上层 HC4067_2 通道） | HC4067_2 SIG/S0~S3/EN/VCC/GND（8pin）+ 16 通道（16pin） |

---

## 3.2 电源树（最终版）

```
DC1 输入 12V
   ↓
SW6 主开关 → +12V_SW
   ├──► MP2315 (U39, FB=100kΩ/8.2kΩ) → +10V_MOTOR  → TB6612 ×3 的 VM
   │     ⚠️ L2 (10µH) 焊位手动短接，不焊电感
   │
   └──► 外部降压模块 (LM2596 / MP1584) → +5V
         ├──► WS2812B ×25 (VDD)
         └──► AMS1117-3.3 (U4) → +3V3_LOGIC
                   └──► Teensy 4.1 / TCA9548A / OLED ×5 / HC4067 ×2 VCC / TB6612 ×3 VCC+STBY
```

**双地分离**：

- `GND`（数字地）= MCU / I²C / 编码器 / 逻辑信号
- `GND_fader`（模拟+电机地）= 推子电位器 / TB6612 VM 回流
- 两者通过磁珠 `BLM18PG121SN1D` (L1) 连接，隔离电机噪声

---

## 3.3 引脚分配表（Teensy 4.1）

| Teensy 引脚 | 功能 | 方向 | 说明 |
|---|---|---|---|
| 0 | ENC1_A | IN | Encoder1 A相（100nF 去抖） |
| 1 | ENC1_B | IN | Encoder1 B相（100nF 去抖） |
| 2 | ENC2_A | IN | Encoder2 A相 |
| 3 | ENC2_B | IN | Encoder2 B相 |
| 4 | ENC3_A | IN | Encoder3 A相 |
| 5 | ENC3_B | IN | Encoder3 B相 |
| 6 | ENC4_A | IN | Encoder4 A相 |
| 7 | ENC4_B | IN | Encoder4 B相 |
| 8 | ENC5_A | IN | Encoder5 A相 |
| 9 | ENC5_B | IN | Encoder5 B相 |
| 10 | WS2812B DATA | OUT | 330Ω 串联限流电阻 → LED1 DIN |
| 11 | HC4067_1 SIG | IN (PULLUP) | 内部上拉，无外部上拉电阻 |
| 12 | HC4067_2 SIG | IN (PULLUP) | 内部上拉，无外部上拉电阻 |
| 13 | MTR4_PWM (PWMB) | OUT | TB6612_2 PWMB |
| 14 (A0) | FADER1_ADC | IN | Fader1 电位器 Wiper |
| 15 (A1) | FADER2_ADC | IN | Fader2 电位器 Wiper |
| 16 (A2) | FADER3_ADC | IN | Fader3 电位器 Wiper |
| 17 (A3) | FADER4_ADC | IN | Fader4 电位器 Wiper |
| 18 | I2C_SDA | I2C | 4.7kΩ 上拉至 3.3V |
| 19 | I2C_SCL | I2C | 4.7kΩ 上拉至 3.3V |
| 20 (A6) | FADER5_ADC | IN | Fader5 电位器 Wiper |
| 21 | MTR3_PWM (PWMA) | OUT | TB6612_2 PWMA |
| 22 | MTR2_PWM (PWMB) | OUT | TB6612_1 PWMB |
| 23 | MTR1_PWM (PWMA) | OUT | TB6612_1 PWMA |
| 24 | 未使用 | — | 原 HC4067_3 SIG，已取消 |
| 25 | 未使用 | — | 预留 |
| 26 | HC4067_S0 | OUT | 共享选择脚 S0 |
| 27 | HC4067_S1 | OUT | 共享选择脚 S1 |
| 28 | HC4067_S2 | OUT | 共享选择脚 S2 |
| 29 | HC4067_S3 | OUT | 共享选择脚 S3 |
| 31 | MTR5_PWM (PWMA) | OUT | TB6612_3 PWMA |
| 32 | MTR5_IN1 (AIN1) | OUT | TB6612_3 AIN1 |
| 33 | MTR5_IN2 (AIN2) | OUT | TB6612_3 AIN2 |
| 34 | MTR4_IN2 (BIN2) | OUT | TB6612_2 BIN2 |
| 35 | MTR4_IN1 (BIN1) | OUT | TB6612_2 BIN1 |
| 36 | MTR3_IN2 (AIN2) | OUT | TB6612_2 AIN2 |
| 37 | MTR3_IN1 (AIN1) | OUT | TB6612_2 AIN1 |
| 38 | MTR2_IN1 (BIN1) | OUT | TB6612_1 BIN1 |
| 39 | MTR2_IN2 (BIN2) | OUT | TB6612_1 BIN2 |
| 40 | MTR1_IN2 (AIN2) | OUT | TB6612_1 AIN2 |
| 41 | MTR1_IN1 (AIN1) | OUT | TB6612_1 AIN1 |

---

## 3.4 模块接线表

### EC11 编码器 × 5

| 编码器 | A相引脚 | B相引脚 | SW（按键） | 去抖 |
|---|---|---|---|---|
| ENC1 | Pin0 | Pin1 | HC4067_1 C0 | 每路 A/B 各 100nF→GND |
| ENC2 | Pin2 | Pin3 | HC4067_1 C1 | 同上 |
| ENC3 | Pin4 | Pin5 | HC4067_1 C2 | 同上 |
| ENC4 | Pin6 | Pin7 | HC4067_1 C3 | 同上 |
| ENC5 | Pin8 | Pin9 | HC4067_1 C4 | 同上 |

### 推子 × 5（电动电位器）

| 推子 | ADC 引脚 | 模拟通道 | 电位器接法 |
|---|---|---|---|
| Fader1 | Pin14 | A0 | Pin1=GND, Pin3=3.3V, Pin2(Wiper)→Teensy |
| Fader2 | Pin15 | A1 | 同上 |
| Fader3 | Pin16 | A2 | 同上 |
| Fader4 | Pin17 | A3 | 同上 |
| Fader5 | Pin20 | A6 | 同上 |

每路 Wiper 并联 100nF→GND 滤波电容。

### TB6612 电机驱动模块 × 3

**公共接法**：VM = +10V_MOTOR，VCC = STBY = +3V3_LOGIC，GND = GND_fader

#### TB6612_1（驱动 Fader1 A通道 + Fader2 B通道）

| 信号 | Teensy 引脚 | TB6612 脚 |
|---|---|---|
| MTR1_PWM | Pin23 | PWMA |
| MTR1_IN1 | Pin41 | AIN1 |
| MTR1_IN2 | Pin40 | AIN2 |
| MTR2_PWM | Pin22 | PWMB |
| MTR2_IN1 | Pin38 | BIN1 |
| MTR2_IN2 | Pin39 | BIN2 |

输出：AO1/AO2 → Fader1 电机；BO1/BO2 → Fader2 电机

#### TB6612_2（驱动 Fader3 A通道 + Fader4 B通道）

| 信号 | Teensy 引脚 | TB6612 脚 |
|---|---|---|
| MTR3_PWM | Pin21 | PWMA |
| MTR3_IN1 | Pin37 | AIN1 |
| MTR3_IN2 | Pin36 | AIN2 |
| MTR4_PWM | Pin13 | PWMB |
| MTR4_IN1 | Pin35 | BIN1 |
| MTR4_IN2 | Pin34 | BIN2 |

#### TB6612_3（驱动 Fader5，仅 A 通道，B 通道空置）

| 信号 | Teensy 引脚 | TB6612 脚 |
|---|---|---|
| MTR5_PWM | Pin31 | PWMA |
| MTR5_IN1 | Pin32 | AIN1 |
| MTR5_IN2 | Pin33 | AIN2 |

> ⚠️ B 通道（BIN1/BIN2/PWMB）完全空置，**必须手动飞线接 GND_fader**（见 3.7 装配前必读）。

#### TB6612 H 桥真值表

| IN1 | IN2 | PWM | 动作 |
|---|---|---|---|
| 1 | 0 | duty | 正转（推子向上） |
| 0 | 1 | duty | 反转（推子向下） |
| 1 | 1 | × | 刹车（短路制动） |
| 0 | 0 | 0 | 滑行（断开） |

### HC4067 多路复用器模块 × 2

**模块型号**：淘宝蓝色 CD74HC4067 模块（自带 EN 引出 + 去耦电容）  
**共享控制脚**：S0=Pin26，S1=Pin27，S2=Pin28，S3=Pin29  
**EN = GND（常开，在模块上飞线或 PCB 接 GND）**，**VCC = 3.3V**

| 芯片 | SIG 引脚 | 模式 |
|---|---|---|
| HC4067_1 | Pin11（INPUT_PULLUP）| 编码器按键 + Strip1~3 按钮 |
| HC4067_2 | Pin12（INPUT_PULLUP）| Strip3 DYN + Strip4~5 按钮（C9~C15 预留）|

### TCA9548A I²C 多路复用器

**芯片封装**：TSSOP-24 裸芯片  
**I²C 地址**：0x70（A0/A1/A2 全接 GND）  
**RESET#**：接 3.3V（常态使能）  
**SDA/SCL**：Pin18/Pin19（4.7kΩ 上拉至 3.3V）

| TCA9548A 通道 | 连接 OLED | 对应 Strip |
|---|---|---|
| 0 | OLED1 (0x3C) | Strip1 |
| 1 | OLED2 (0x3C) | Strip2 |
| 2 | OLED3 (0x3C) | Strip3 |
| 3 | OLED4 (0x3C) | Strip4 |
| 4 | OLED5 (0x3C) | Strip5 |

### OLED × 5（SSD1306 128×64）

**型号**：SSD1306，地址 0x3C  
**VCC = 3.3V**，**SDA/SCL** 经 TCA9548A 分通道访问

### WS2812B LED × 25

**数据线**：Pin10 → R9 (330Ω 限流) → U43 DIN  
**VDD = +5V**，**GND = 数字地**

---

## 3.5 按键映射表（最终版）

### HC4067_1（SIG=Pin11，16 通道全部使用）

| 通道 | 功能 | 说明 |
|---|---|---|
| C0 | ENC1_SW | 编码器1 单击/双击 |
| C1 | ENC2_SW | 编码器2 单击/双击 |
| C2 | ENC3_SW | 编码器3 单击/双击 |
| C3 | ENC4_SW | 编码器4 单击/双击 |
| C4 | ENC5_SW | 编码器5 单击/双击 |
| C5 | Strip1 MUTE | 按键1 |
| C6 | Strip1 SOLO | 按键2 |
| C7 | Strip1 SELECT | 按键3 |
| C8 | Strip1 DYN | 按键4 |
| C9 | Strip2 MUTE | 按键5 |
| C10 | Strip2 SOLO | 按键6 |
| C11 | Strip2 SELECT | 按键7 |
| C12 | Strip2 DYN | 按键8 |
| C13 | Strip3 MUTE | 按键9 |
| C14 | Strip3 SOLO | 按键10 |
| C15 | Strip3 SELECT | 按键11 |

### HC4067_2（SIG=Pin12，C0~C8 使用，C9~C15 预留）

| 通道 | 功能 | 说明 |
|---|---|---|
| C0 | Strip3 DYN | 按键12 |
| C1 | Strip4 MUTE | 按键13 |
| C2 | Strip4 SOLO | 按键14 |
| C3 | Strip4 SELECT | 按键15 |
| C4 | Strip4 DYN | 按键16 |
| C5 | Strip5 MUTE | 按键17 |
| C6 | Strip5 SOLO | 按键18 |
| C7 | Strip5 SELECT | 按键19 |
| C8 | Strip5 DYN | 按键20 |
| C9~C15 | **预留备用** | PCB 上不焊按键，固件不扫描，不触发任何回调 |

---

## 3.6 WS2812B LED 编号映射

25 颗 LED 蛇形串联，每 5 颗对应一个推子条：

| LED 编号 | 对应 Strip | PCB 位号 |
|---|---|---|
| LED 0~4 | Strip1 | U43~U47 |
| LED 5~9 | Strip2 | U48~U52 |
| LED 10~14 | Strip3 | U53~U57 |
| LED 15~19 | Strip4 | U58~U62 |
| LED 20~24 | Strip5 | U63~U67 |

**数据链路**：Teensy Pin10 → R9 (330Ω 限流) → U43 DIN → … → U67 DOUT（串联）

---

## 3.7 ⚠️ 装配前必读

**以下 3 项为必做手动操作，缺少任何一项将导致硬件故障：**

### ✅ 必做 1：L2 焊位短接

MP2315 (U39) 输入侧的 10µH 电感 **L2 不要焊接**，用 0Ω 跳线或飞线短接两个焊盘。

**原因**：避免输入端 LC 谐振影响 MP2315 稳定性。

```
L2 焊位：  ○————[短接]————○
              （飞线或 0Ω 跳线）
```

### ✅ 必做 2：TB6612_3（U13/U14）B 通道悬空脚飞线

第三片 TB6612 模块只使用 A 通道驱动 Fader5，**B 通道完全空置**。

**必须**用飞线把 **BIN1 / BIN2 / PWMB** 三个引脚接到 **GND_fader**，避免 CMOS 输入悬空导致芯片误动作和发热。

```
TB6612_3 (U14 控制侧右排):
  Pin5 (BIN1) ── 飞线 ──┐
  Pin6 (BIN2) ── 飞线 ──┼── GND_fader
  Pin7 (PWMB) ── 飞线 ──┘
```

> ⚠️ **注意**：STBY（右排 Pin4）必须保持接 3.3V，**不要误接 GND**！

### ✅ 必做 3：HC4067_2（U28）备用按键焊位不焊

上层面板 PCB 备用按键焊位（按键 21~25，对应 HC4067_2 C9~C15）保持空焊，固件不扫描这些通道。

---

**以下 2 项为建议加强（非必须）：**

### 建议 4：修正重复电容编号

PCB 软件中执行「自动重新标号」，修正所有重复 C10 的电容编号（编码器去抖电容 + WS2812 退耦电容存在重号）。

### 建议 5：外部降压模块输入接至 SW6 之后

外部 5V 降压模块的 12V 输入端，建议接到 SW6 之后的 +12V_SW 网络，让总开关同时控制所有电源。

---

## 3.8 上电测试顺序

1. **不插 Teensy 4.1**，先上电，用万用表确认：
   - +12V_SW、+10V_MOTOR、+5V、+3.3V 输出正常
   - 各电源对地无短路

2. **插入 Teensy 4.1，先不接电机**：
   - 烧录固件
   - 确认 OLED 点亮（5 块）
   - 测试编码器旋转/按下响应
   - 测试 WS2812B LED 亮起

3. **接入电机**，逐个推子测试：
   - 自动归位功能
   - 用户触摸检测（电机停止对抗）
   - MIDI 输出（在 DAW 中确认 CC7 接收）

---

## 3.9 模块使用确认

| 模块 | 规格 | 来源 | 关键说明 |
|---|---|---|---|
| TB6612 × 3 | 淘宝**红色模块板** | 淘宝 | 自带 STBY 引出 + 输出去耦 + 续流二极管。STBY 必须接 3.3V |
| HC4067 × 2 | 淘宝**蓝色 CD74HC4067 模块** | 淘宝 | 自带 EN 引出 + 去耦电容。EN 接 GND（常开） |
| TCA9548A | TSSOP-24 裸芯片 | — | A0/A1/A2 全接 GND（地址 = 0x70），RESET# 接 3.3V |
| AMS1117-3.3 | SOT-223 | — | VIN 接外部降压模块 +5V 输出 |
| MP2315 | — | — | 升压至 +10V 驱动电机，L2 焊位短接不焊电感 |

---

## 3.10 已知已修正的错误（变更日志）

以下问题在 PCB 审查过程中发现并已修正：

| # | 问题 | 状态 |
|---|---|---|
| 1 | AMS1117 (U4) VIN 之前接错（非 5V）| ✅ 已修正为接外部降压模块 +5V 输出 |
| 2 | TCA9548A RESET# 曾被误读为接 GND | ✅ 确认原理图就是接 3.3V，无需修改 |
| 3 | 编码器 A/B 去抖电容缺失 | ✅ 已补加 100nF→GND（每个编码器 2 颗，共 10 颗） |
| 4 | HC4067_3 第三片计划（Pin24）| ✅ 已确认不安装，固件已清理相关代码 |
| 5 | TB6612_3 B 通道输入悬空 | ⚠️ 原理图 B 通道未接 GND，需**手动飞线**（见 3.7 必做 2） |
