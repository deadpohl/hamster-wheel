// Hamster wheel desk toy: plays an animation on a GC9A01 round display.
// Author: DeadPohl  https://www.instagram.com/_deadpohl_
//
// The animation is a single file, assets/animation.bin, linked into the firmware
// (build it with tools/make_animation.py). Format: see that script.

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <TJpg_Decoder.h>

#include "config.h"

extern const uint8_t animation_start[] asm("_binary_assets_animation_bin_start");
extern const uint8_t animation_end[] asm("_binary_assets_animation_bin_end");

struct Header {
  char magic[4];
  uint16_t count, width, height, reserved;
};
struct Entry {
  uint32_t offset, size;
  uint16_t delayMs, reserved;
};

static TFT_eSPI tft;
static uint16_t frameCount = 0;

// Flash data may be unaligned, so always copy before reading fields.
static Entry readEntry(uint16_t i) {
  Entry e;
  memcpy(&e, animation_start + sizeof(Header) + sizeof(Entry) * i, sizeof(e));
  return e;
}

static bool pushBlock(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t *bitmap) {
  if (y >= tft.height()) return false;
  tft.pushImage(x, y, w, h, bitmap);
  return true;
}

static void showMessage(const char *line1, const char *line2) {
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.drawString(line1, tft.width() / 2, tft.height() / 2 - 10, 2);
  tft.drawString(line2, tft.width() / 2, tft.height() / 2 + 10, 2);
}

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(SCREEN_ROTATION);
  tft.setSwapBytes(true);
  tft.fillScreen(TFT_BLACK);

  TJpgDec.setJpgScale(1);
  // No TJpgDec.setSwapBytes() here: TFT_eSPI already swaps the bytes (tft.setSwapBytes above),
  // doing it twice scrambles the colours.
  TJpgDec.setCallback(pushBlock);

  Header h;
  size_t len = animation_end - animation_start;
  if (len < sizeof(Header)) {
    showMessage("NO ANIMATION", "see tools/make_animation.py");
    Serial.println("animation.bin is missing or empty");
    return;
  }
  memcpy(&h, animation_start, sizeof(h));
  if (memcmp(h.magic, "HWA1", 4) != 0 || h.count == 0) {
    showMessage("BAD ANIMATION", "rebuild animation.bin");
    Serial.println("animation.bin has a bad header");
    return;
  }
  frameCount = h.count;
  Serial.printf("hamster-wheel: %u frames, %u KB\n", frameCount, (unsigned)(len / 1024));
}

void loop() {
  if (frameCount == 0) {
    delay(1000);
    return;
  }

  static uint16_t frame = 0;
  static uint32_t nextAt = 0, statStart = 0, statFrames = 0;

  Entry e = readEntry(frame);
  TJpgDec.drawJpg(0, 0, animation_start + e.offset, e.size);

  // Fixed pacing: wait until the frame's display time has passed. If decoding
  // was slower than that, just carry on (no catching up).
  uint32_t now = millis();
  if (nextAt == 0) nextAt = now;
  nextAt += max<uint16_t>(e.delayMs, MIN_FRAME_MS);
  if ((int32_t)(nextAt - now) > 0) {
    delay(nextAt - now);
  } else {
    nextAt = now;
  }

  frame = (frame + 1) % frameCount;

  statFrames++;
  if (now - statStart >= STATS_EVERY_MS) {
    if (statStart != 0) Serial.printf("%.1f fps\n", statFrames * 1000.0f / (now - statStart));
    statStart = now;
    statFrames = 0;
  }
}
