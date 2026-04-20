# firmware/README.md

# Teensy 4.1 混音台控制器固件

本目录是 Python 模拟器（`mixer_simulator/`）对应的 **Teensy 4.1 实体硬件固件**。固件行为、状态机、MIDI 协议与 Python 模拟器完全一致。

---

## 目录结构

```
firmware/
├── platformio.ini          # PlatformIO 配置
├── README.md               # 本文件
├── HARDWARE.md             # 完整接线表
├── PYTHON_PARITY.md        # Python 模拟器 ↔ 固件行为对照表
└── src/
    ├── main.cpp            # setup() / loop()
    ├── pin_config.h        # 所有引脚常量
    ├── default_names.h     # 默认通道名称表（32 项）
    ├── mixer_state.h/.cpp  # 状态机（144 通道 + 5 条 strip）
    ├── midi_io.h/.cpp      # USB MIDI 收发
    ├── fader_driver.h/.cpp # ADC + 电机闭环控制
    ├── encoder_input.h/.cpp# EC11 编码器解码
    ├── hc4067_scanner.h/.cpp # HC4067 扫描 + 事件检测
    ├── button_input.h/.cpp # 按键 → MixerState 映射
    ├── oled_display.h/.cpp # TCA9548A + SSD1306 OLED
    └── led_feedback.h/.cpp # WS2812B LED 状态反馈
```

---

## 编译方法

### 推荐：PlatformIO

1. 安装 [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/) 或 VS Code PlatformIO 插件
2. 进入 `firmware/` 目录：
   ```bash
   cd firmware
   pio run
   ```
3. 编译成功后，`.pio/build/teensy41/firmware.hex` 即为烧录文件

### 备选：Arduino IDE 2.x

1. 安装 Teensyduino（从 [pjrc.com](https://www.pjrc.com/teensy/td_download.html) 下载）
2. 在 Arduino IDE 中：
   - 开发板 → **Teensy 4.1**
   - USB 类型 → **Serial + MIDI**
3. 打开 `firmware/src/main.cpp`（需将扩展名改为 `.ino` 或使用 src-layout 插件）
4. 安装以下库：
   - `Encoder`（Paul Stoffregen）
   - `Adafruit GFX Library`
   - `Adafruit SSD1306`
   - `FastLED`

---

## 烧录步骤

### PlatformIO
```bash
cd firmware
pio run --target upload
```

### Teensy Loader（手动）
1. 按 Teensy 板上的复位按钮，进入 Bootloader 模式
2. 用 Teensy Loader 打开 `.pio/build/teensy41/firmware.hex`
3. 点击 "Program" 完成烧录

---

## USB MIDI 设备名说明

烧录后，连接 Teensy 至电脑，系统会识别到：
- **串口设备**：`/dev/ttyACM0`（Linux）/ `COM?`（Windows）/ `/dev/cu.usbmodem*`（macOS）
- **MIDI 设备**：`Teensy MIDI`（出现在 DAW 的 MIDI 输入/输出列表中）

> Teensy 4.1 使用内置 USB MIDI，无需额外驱动（macOS/Linux 即插即用；Windows 需 Teensyduino 驱动）。

---

## 故障排查

### OLED 无显示
1. 检查 I2C 接线：`Pin18=SDA`，`Pin19=SCL`，4.7kΩ 上拉至 3.3V
2. 用 I2C 扫描程序确认 TCA9548A 地址 `0x70` 和 SSD1306 地址 `0x3C` 可见
3. 检查 TCA9548A 的 A0/A1/A2 地址脚是否均接 GND（地址 = 0x70）
4. 确认 OLED VCC 接 3.3V，GND 接 GND

### 推子不动
1. 检查 TB6612 STBY 脚是否接 3.3V（低电平 = 芯片禁用）
2. 用万用表测量 VM（应为 10V）和 VCC（应为 3.3V）
3. 检查 PWM/IN1/IN2 引脚接线是否与 `pin_config.h` 一致
4. 串口监视器查看固件启动日志，确认无初始化错误

### 编码器跳动（值不稳定）
1. 检查 A/B 引脚是否有 100nF 电容到 GND（硬件去抖）
2. 检查 10kΩ 上拉至 3.3V 是否存在
3. 调整 `encoder_input.cpp` 中的 `ACCEL_FAST_MS` 参数

### 按键无响应
1. 检查 HC4067 的 EN 脚是否接 GND（HIGH = 禁用输出）
2. 检查 S0~S3 共享脚 `Pin26~29` 接线
3. 用示波器或逻辑分析仪检查 SIG 引脚在按键按下时是否变低

### MIDI 无输出
1. 确认 Arduino IDE / PlatformIO 配置中 USB 类型为 `Serial + MIDI`
2. 在 DAW 中激活 `Teensy MIDI` 设备
3. 串口监视器查看 MIDI 发送日志（`[MidiIO]` 开头的消息）

---

## 硬件信息

详见 [`HARDWARE.md`](HARDWARE.md)。

> ⚠️ **装配前必读**：上电前请务必确认 [`HARDWARE.md` 装配前必读](HARDWARE.md#37-️-装配前必读)中的 **3 项必做手动操作**（L2 短接、TB6612 #3 B 通道飞线、HC4067_2 备用焊位不焊）。

## Python 模拟器对照

详见 [`PYTHON_PARITY.md`](PYTHON_PARITY.md)。
