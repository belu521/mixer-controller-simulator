# firmware/lib/README.md

# 第三方库说明

本目录用于放置本地修改过的第三方库（如有）。  
标准依赖库直接在 `platformio.ini` 中声明，PlatformIO 会自动下载：

| 库名 | 版本 | 用途 |
|---|---|---|
| `paulstoffregen/Encoder` | ^1.4.4 | EC11 编码器解码（Paul Stoffregen 官方库）|
| `adafruit/Adafruit GFX Library` | ^1.11.9 | OLED 图形渲染基础库 |
| `adafruit/Adafruit SSD1306` | ^2.5.9 | SSD1306 OLED 驱动 |
| `fastled/FastLED` | ^3.6.0 | WS2812B LED 控制 |

如需使用本地修改版本，将库文件夹放入此 `lib/` 目录即可。
