# PlatformIO post script: also produce one merged image that can be flashed at
# address 0x0 from a browser (no PlatformIO needed).
# Author: DeadPohl  https://www.instagram.com/_deadpohl_
Import("env")

APP_BIN = "$BUILD_DIR/${PROGNAME}.bin"
MERGED_BIN = "$BUILD_DIR/hamster-wheel-esp32.bin"
BOARD = env.BoardConfig()


def merge_bin(source, target, env):
    images = env.Flatten(env.get("FLASH_EXTRA_IMAGES", [])) + ["$ESP32_APP_OFFSET", APP_BIN]
    cmd = " ".join(
        ['"$PYTHONEXE"', '"$OBJCOPY"', "--chip", BOARD.get("build.mcu", "esp32"), "merge_bin",
         "--flash_mode", BOARD.get("build.flash_mode", "dio"),
         "--flash_freq", BOARD.get("build.f_flash", "40000000L")[:-7] + "m",
         "--flash_size", BOARD.get("upload.flash_size", "4MB"),
         "-o", MERGED_BIN] + images)
    env.Execute(env.VerboseAction(cmd, "Merging into hamster-wheel-esp32.bin"))


env.AddPostAction(APP_BIN, merge_bin)
