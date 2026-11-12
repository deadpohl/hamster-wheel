// Hamster wheel desk toy: user settings.
// Author: DeadPohl  https://www.instagram.com/_deadpohl_
// Pins and the display driver live in platformio.ini (build_flags).
#pragma once

// Screen orientation, 0 to 3. Change it if the picture is rotated on your build.
#define SCREEN_ROTATION 0

// Fastest allowed frame time in ms. The real delay of each frame comes from
// animation.bin (see tools/make_animation.py), this is only a lower limit.
#define MIN_FRAME_MS 15

// Print the measured frame rate on the serial port every few seconds.
#define STATS_EVERY_MS 5000
