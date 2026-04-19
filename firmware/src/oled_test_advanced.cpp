// firmware/src/oled_test_advanced.cpp
// ═══════════════════════════════════════════════════════════════
// OLED 高阶诊断测试（独立 sketch）
// 用途：排查 SSD1306 闪屏 / 花屏 / I2C 通信故障
// 硬件：Teensy 4.1 + TCA9548A (0x70) + 5×SSD1306 (0x3C)
// 使用方法：
//   1. 将下方 #if 0 改为 #if 1，同时注释掉 main.cpp 中的
//      setup()/loop()（避免重复定义）。
//   2. 编译上传后打开串口监视器 (115200)，按提示操作。
// ═══════════════════════════════════════════════════════════════
//
// 若要编译此文件为主程序，请取消下方 #if 1 的注释，
// 同时将 main.cpp 中的 setup()/loop() 注释掉（避免重复定义）。
// 日常构建时保持 #if 0 即可与 main.cpp 共存。

#if 0  // ← 改为 1 以启用本测试；保持 0 时不参与编译

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ─────────────────────── 硬件常量 ───────────────────────
constexpr uint8_t TCA_ADDR   = 0x70;
constexpr uint8_t OLED_ADDR  = 0x3C;
constexpr uint8_t OLED_W     = 128;
constexpr uint8_t OLED_H     = 64;
constexpr int8_t  OLED_RST   = -1;
constexpr uint8_t NUM_OLEDS  = 5;

static Adafruit_SSD1306 disp[NUM_OLEDS] = {
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
    Adafruit_SSD1306(OLED_W, OLED_H, &Wire, OLED_RST),
};

// ─────────────── TCA9548A 通道选择 ──────────────────────
static void tcaSelect(uint8_t ch) {
    Wire.beginTransmission(TCA_ADDR);
    Wire.write(1 << ch);
    Wire.endTransmission();
}

// ─────────────── 初始化所有屏幕 ─────────────────────────
static bool initAllDisplays() {
    bool allOk = true;
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        if (!disp[i].begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
            Serial.printf("  [FAIL] OLED %u init failed\n", i);
            allOk = false;
        } else {
            disp[i].clearDisplay();
            disp[i].setTextColor(SSD1306_WHITE);
            disp[i].display();
            Serial.printf("  [OK]   OLED %u ready\n", i);
        }
    }
    return allOk;
}

// ─────────────── 辅助：在指定屏上显示文字 ────────────────
static void showText(uint8_t idx, const char* line1,
                     const char* line2 = nullptr,
                     const char* line3 = nullptr) {
    tcaSelect(idx);
    Adafruit_SSD1306& d = disp[idx];
    d.clearDisplay();
    d.setTextSize(1);
    d.setCursor(0, 0);
    d.print(line1);
    if (line2) { d.setCursor(0, 16); d.print(line2); }
    if (line3) { d.setCursor(0, 32); d.print(line3); }
    d.display();
}

// ─────────────── 辅助：等待串口任意输入继续 ──────────────
static void waitSerial(const char* prompt) {
    Serial.println(prompt);
    while (!Serial.available()) { delay(10); }
    while (Serial.available()) { Serial.read(); } // 清空缓冲
}

// ═══════════════════════════════════════════════════════════
// 测试 1：I2C 总线扫描
// 检测 TCA9548A 及每个通道上的 OLED 是否响应
// ═══════════════════════════════════════════════════════════
static void test1_i2cScan() {
    Serial.println("\n========== TEST 1: I2C Bus Scan ==========");

    // 扫描主总线
    Serial.println("--- Main bus scan ---");
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0) {
            Serial.printf("  Found device at 0x%02X", addr);
            if (addr == TCA_ADDR) Serial.print(" (TCA9548A)");
            Serial.println();
        }
    }

    // 逐通道扫描
    for (uint8_t ch = 0; ch < 8; ch++) {
        tcaSelect(ch);
        Serial.printf("--- TCA ch%u ---\n", ch);
        bool found = false;
        for (uint8_t addr = 1; addr < 127; addr++) {
            if (addr == TCA_ADDR) continue; // 跳过 TCA 自身
            Wire.beginTransmission(addr);
            if (Wire.endTransmission() == 0) {
                Serial.printf("  0x%02X", addr);
                if (addr == OLED_ADDR) Serial.print(" (SSD1306)");
                Serial.println();
                found = true;
            }
        }
        if (!found) Serial.println("  (empty)");
    }
    Serial.println("TEST 1 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 2：全屏填充 / 清除压力测试（检测闪屏频率）
// 反复全白↔全黑，串口输出每屏刷新时间
// ═══════════════════════════════════════════════════════════
static void test2_fillClearStress() {
    Serial.println("\n========== TEST 2: Fill/Clear Stress ==========");
    Serial.println("Each OLED: 20 cycles full-white <-> full-black");

    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        unsigned long totalUs = 0;
        for (int c = 0; c < 20; c++) {
            unsigned long t0 = micros();
            disp[i].fillScreen(SSD1306_WHITE);
            disp[i].display();
            disp[i].fillScreen(SSD1306_BLACK);
            disp[i].display();
            totalUs += (micros() - t0);
        }
        float avgMs = (float)totalUs / 20.0f / 1000.0f;
        Serial.printf("  OLED %u: avg %.2f ms/cycle (40 display() calls)\n",
                       i, avgMs);
    }
    Serial.println("TEST 2 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 3：I2C 时钟速度对比
// 100kHz / 400kHz / 1MHz 下分别测量单帧刷新时间
// 如果闪屏只在高速时出现，说明布线/上拉问题
// ═══════════════════════════════════════════════════════════
static void test3_clockSpeedCompare() {
    Serial.println("\n========== TEST 3: I2C Clock Speed Compare ==========");

    static const uint32_t speeds[] = { 100000, 400000, 1000000 };
    static const char* labels[]    = { "100kHz", "400kHz", "1MHz" };

    for (int s = 0; s < 3; s++) {
        Wire.setClock(speeds[s]);
        delay(10);
        Serial.printf("--- %s ---\n", labels[s]);

        for (uint8_t i = 0; i < NUM_OLEDS; i++) {
            tcaSelect(i);
            disp[i].clearDisplay();
            disp[i].setTextSize(2);
            disp[i].setCursor(10, 20);
            disp[i].printf("OLED%u", i);

            unsigned long t0 = micros();
            disp[i].display();
            unsigned long dt = micros() - t0;

            Serial.printf("  OLED %u: %lu us (%.2f ms)\n",
                           i, dt, (float)dt / 1000.0f);
        }
    }

    // 恢复 400kHz
    Wire.setClock(400000);
    Serial.println("TEST 3 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 4：棋盘格 + 反色 滚动模式测试
// 用来观察是否某些特定像素区域闪烁（硬件接触不良）
// ═══════════════════════════════════════════════════════════
static void test4_checkerboard() {
    Serial.println("\n========== TEST 4: Checkerboard Pattern ==========");
    Serial.println("Displaying checkerboard, then inverted. Watch for flicker.");

    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        Adafruit_SSD1306& d = disp[i];

        // 棋盘格 8×8
        d.clearDisplay();
        for (int y = 0; y < OLED_H; y++) {
            for (int x = 0; x < OLED_W; x++) {
                if (((x / 8) + (y / 8)) % 2 == 0)
                    d.drawPixel(x, y, SSD1306_WHITE);
            }
        }
        d.display();
    }

    delay(2000);

    // 反色
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].invertDisplay(true);
    }

    delay(2000);

    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].invertDisplay(false);
    }
    Serial.println("TEST 4 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 5：逐屏独占刷新 vs 轮询刷新（隔离闪烁源）
// 只刷新 1 块屏，其余保持静态，看是否仍闪
// ═══════════════════════════════════════════════════════════
static void test5_isolatedRefresh() {
    Serial.println("\n========== TEST 5: Isolated Refresh ==========");
    Serial.println("Only one OLED refreshes at a time. Others stay static.");

    // 先在所有屏上画一个静态画面
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        showText(i, "STATIC", "If this", "flickers: HW");
    }
    delay(1000);

    for (uint8_t active = 0; active < NUM_OLEDS; active++) {
        Serial.printf("  Refreshing ONLY OLED %u (30 frames)...\n", active);
        for (int f = 0; f < 30; f++) {
            tcaSelect(active);
            Adafruit_SSD1306& d = disp[active];
            d.clearDisplay();
            d.setTextSize(1);
            d.setCursor(0, 0);
            d.printf("OLED %u  frame %d", active, f);

            // 动画：水平线扫描
            int lineY = (f * 2) % OLED_H;
            d.drawFastHLine(0, lineY, OLED_W, SSD1306_WHITE);
            d.display();
            delay(50);
        }
    }
    Serial.println("TEST 5 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 6：高速动画 FPS 基准（粒子系统）
// 15 个粒子 + 近邻连线，持续 5 秒，输出平均 FPS
// 如果 FPS 过低或不稳定，可能是 I2C 带宽饱和导致闪烁
// ═══════════════════════════════════════════════════════════

struct Particle {
    float x, y, vx, vy;
};

static void test6_particleFPS() {
    Serial.println("\n========== TEST 6: Particle Animation FPS ==========");
    Serial.println("Running particle system on each OLED for 5 seconds...");

    constexpr int NP = 15;
    Particle particles[NP];

    for (uint8_t idx = 0; idx < NUM_OLEDS; idx++) {
        // 初始化粒子
        randomSeed(analogRead(A0) + idx * 37);
        for (int p = 0; p < NP; p++) {
            particles[p].x  = random(OLED_W);
            particles[p].y  = random(OLED_H);
            particles[p].vx = (random(10) - 5) * 0.5f;
            particles[p].vy = (random(10) - 5) * 0.5f;
            if (particles[p].vx == 0) particles[p].vx = 0.5f;
            if (particles[p].vy == 0) particles[p].vy = 0.5f;
        }

        tcaSelect(idx);
        unsigned long startMs = millis();
        uint32_t frames = 0;

        while (millis() - startMs < 5000) {
            Adafruit_SSD1306& d = disp[idx];
            d.clearDisplay();

            // 更新与绘制
            for (int p = 0; p < NP; p++) {
                particles[p].x += particles[p].vx;
                particles[p].y += particles[p].vy;
                if (particles[p].x < 0 || particles[p].x >= OLED_W)
                    particles[p].vx *= -1;
                if (particles[p].y < 0 || particles[p].y >= OLED_H)
                    particles[p].vy *= -1;
                particles[p].x = constrain(particles[p].x, 0, OLED_W - 1);
                particles[p].y = constrain(particles[p].y, 0, OLED_H - 1);

                d.drawPixel((int)particles[p].x, (int)particles[p].y,
                            SSD1306_WHITE);

                // 近邻连线（距离 < 25px）
                for (int q = p + 1; q < NP; q++) {
                    float dx = particles[p].x - particles[q].x;
                    float dy = particles[p].y - particles[q].y;
                    if (dx * dx + dy * dy < 625.0f) {
                        d.drawLine((int)particles[p].x, (int)particles[p].y,
                                   (int)particles[q].x, (int)particles[q].y,
                                   SSD1306_WHITE);
                    }
                }
            }

            // FPS 显示
            d.setTextSize(1);
            d.setCursor(0, 0);
            uint32_t elapsed = millis() - startMs;
            if (elapsed > 0) {
                d.printf("FPS:%lu", frames * 1000UL / elapsed);
            }
            d.display();
            frames++;
        }

        float avgFps = (float)frames / 5.0f;
        Serial.printf("  OLED %u: %lu frames in 5s → %.1f FPS\n",
                       idx, frames, avgFps);
    }
    Serial.println("TEST 6 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 7：对比度 / VCOMH 调节测试
// SSD1306 的对比度和 VCOMH 设置会影响亮度和闪烁
// ═══════════════════════════════════════════════════════════
static void test7_contrastSweep() {
    Serial.println("\n========== TEST 7: Contrast & VCOMH Sweep ==========");
    Serial.println("Sweeping contrast 0x00 → 0xFF on all OLEDs...");

    // 先画一个半填充画面用于观察
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        Adafruit_SSD1306& d = disp[i];
        d.clearDisplay();
        d.setTextSize(2);
        d.setCursor(10, 10);
        d.printf("OLED%u", i);
        d.fillRect(0, 40, 128, 24, SSD1306_WHITE);
        d.display();
    }

    // 对比度从低到高再到低
    for (int pass = 0; pass < 2; pass++) {
        for (int c = 0; c <= 255; c += 5) {
            uint8_t val = (pass == 0) ? (uint8_t)c : (uint8_t)(255 - c);
            for (uint8_t i = 0; i < NUM_OLEDS; i++) {
                tcaSelect(i);
                disp[i].ssd1306_command(SSD1306_SETCONTRAST);
                disp[i].ssd1306_command(val);
            }
            delay(30);
        }
    }

    // 恢复默认对比度 0xCF
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].ssd1306_command(SSD1306_SETCONTRAST);
        disp[i].ssd1306_command(0xCF);
    }
    Serial.println("TEST 7 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// 测试 8：电源稳定性探测（静态画面长时间观察）
// 全白 → 10秒 → 全黑 → 10秒 → 半白半黑 → 10秒
// 如果在静态画面下仍闪烁，几乎可确定是电源或接线问题
// ═══════════════════════════════════════════════════════════
static void test8_powerStability() {
    Serial.println("\n========== TEST 8: Power Stability (30s) ==========");
    Serial.println("Static screens — watch for flicker without any I2C traffic.");

    // 全白
    Serial.println("  Phase 1: ALL WHITE (10s)");
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].fillScreen(SSD1306_WHITE);
        disp[i].display();
    }
    delay(10000);

    // 全黑
    Serial.println("  Phase 2: ALL BLACK (10s)");
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].fillScreen(SSD1306_BLACK);
        disp[i].display();
    }
    delay(10000);

    // 半白半黑（上半白，下半黑）
    Serial.println("  Phase 3: HALF WHITE / HALF BLACK (10s)");
    for (uint8_t i = 0; i < NUM_OLEDS; i++) {
        tcaSelect(i);
        disp[i].clearDisplay();
        disp[i].fillRect(0, 0, OLED_W, OLED_H / 2, SSD1306_WHITE);
        disp[i].display();
    }
    delay(10000);

    Serial.println("TEST 8 complete.\n");
}

// ═══════════════════════════════════════════════════════════
// setup() / loop()
// ═══════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(1000); // 给串口足够时间打开
    Serial.println("╔════════════════════════════════════════════════╗");
    Serial.println("║  OLED Advanced Diagnostic Test Suite          ║");
    Serial.println("║  Hardware: Teensy 4.1 + TCA9548A + 5×SSD1306 ║");
    Serial.println("╚════════════════════════════════════════════════╝");

    Wire.begin();
    Wire.setClock(400000);

    Serial.println("\n--- Initializing OLEDs ---");
    initAllDisplays();

    Serial.println("\n=== Running all tests sequentially ===");
    Serial.println("Send any char via Serial to start.\n");

    waitSerial(">>> Press ENTER to begin test suite <<<");
}

void loop() {
    test1_i2cScan();
    waitSerial(">>> ENTER for Test 2 (Fill/Clear Stress) <<<");

    test2_fillClearStress();
    waitSerial(">>> ENTER for Test 3 (I2C Clock Speed) <<<");

    test3_clockSpeedCompare();
    waitSerial(">>> ENTER for Test 4 (Checkerboard) <<<");

    test4_checkerboard();
    waitSerial(">>> ENTER for Test 5 (Isolated Refresh) <<<");

    test5_isolatedRefresh();
    waitSerial(">>> ENTER for Test 6 (Particle FPS) <<<");

    test6_particleFPS();
    waitSerial(">>> ENTER for Test 7 (Contrast Sweep) <<<");

    test7_contrastSweep();
    waitSerial(">>> ENTER for Test 8 (Power Stability) <<<");

    test8_powerStability();

    Serial.println("\n═══════════════════════════════════════════");
    Serial.println("  ALL TESTS COMPLETE");
    Serial.println("═══════════════════════════════════════════");
    Serial.println("\nFlicker Diagnosis Guide:");
    Serial.println("  - Test 8 flickers (static)? → Power/wiring issue");
    Serial.println("  - Test 3: only 1MHz flickers? → I2C pull-up too weak");
    Serial.println("  - Test 5: other screens flicker when not refreshing?");
    Serial.println("    → TCA9548A channel crosstalk or power droop");
    Serial.println("  - Test 2: slow refresh? → I2C bus congestion");
    Serial.println("  - Test 7: flicker at low contrast? → OLED module quality");
    Serial.println("\nSend any char to re-run all tests.\n");

    waitSerial(">>> Press ENTER to re-run <<<");
}

#endif // #if 0
