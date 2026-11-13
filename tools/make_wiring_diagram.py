#!/usr/bin/env python3
"""Draw the wiring diagram used in the README (docs/img/wiring.png).

Author: DeadPohl  https://www.instagram.com/_deadpohl_
Needs matplotlib:  pip install matplotlib
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parent.parent / "docs" / "img" / "wiring.png"

# (label on the display, label on the ESP32 board, wire colour in the drawing)
ROWS = [
    ("RST", "GPIO 16", "printed RX2 on many boards", "#8e44ad"),
    ("CS", "GPIO 5", "printed D5", "#2980b9"),
    ("DC", "GPIO 17", "printed TX2 on many boards", "#16a085"),
    ("SCL", "GPIO 18", "printed D18", "#e67e22"),
    ("SDA", "GPIO 23", "printed D23", "#d35400"),
    ("GND", "GND", "any GND pin", "#222222"),
    ("VCC", "3V3", "printed 3V3 or 3.3V, NOT 5V", "#c0392b"),
]


def main():
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=120)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")

    # boxes
    ax.add_patch(FancyBboxPatch((3, 6), 24, 46, boxstyle="round,pad=0.5,rounding_size=2",
                                fc="#eaf2f8", ec="#34495e", lw=1.6))
    ax.add_patch(FancyBboxPatch((72, 6), 25, 46, boxstyle="round,pad=0.5,rounding_size=2",
                                fc="#e9f7ef", ec="#34495e", lw=1.6))
    ax.text(15, 56.5, "Round display\n(GC9A01, 7 pins)", ha="center", va="center", fontsize=12, weight="bold")
    ax.text(84.5, 56.5, "ESP32 board", ha="center", va="center", fontsize=12, weight="bold")
    ax.text(15, 8.8, "pins in the order\nprinted on the module", ha="center", va="center", fontsize=8.5, color="#555")
    ax.text(84.5, 8.8, "names are printed\nnext to the pins", ha="center", va="center", fontsize=8.5, color="#555")

    top, step = 48, 5.6
    for i, (disp, esp, note, col) in enumerate(ROWS):
        y = top - i * step
        # display pin
        ax.add_patch(Rectangle((24.5, y - 1.6), 4.5, 3.2, fc="#f1c40f", ec="#7d6608", lw=1))
        ax.text(22.5, y, disp, ha="right", va="center", fontsize=12, weight="bold")
        # ESP pin
        ax.add_patch(Rectangle((71, y - 1.6), 4.5, 3.2, fc="#f1c40f", ec="#7d6608", lw=1))
        ax.text(77.5, y + 0.9, esp, ha="left", va="center", fontsize=12, weight="bold")
        ax.text(77.5, y - 1.7, note, ha="left", va="center", fontsize=6.6, color="#555")
        # wire
        ax.plot([29, 71], [y, y], color=col, lw=4.2, solid_capstyle="round", zorder=1)
        ax.text(50, y + 1.5, f"{disp}  to  {esp}", ha="center", va="bottom", fontsize=8.5, color=col, weight="bold")

    ax.text(50, 62.5, "7 jumper wires, any colours: write down which is which",
            ha="center", va="center", fontsize=11, color="#222")
    ax.text(50, 1.6, "Some displays list the pins in the opposite order: always follow the names, not the position.",
            ha="center", va="center", fontsize=8.5, color="#555")
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
