"""Build every printable part, check it, and write the STL files and previews.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Usage (from this folder):
    pip install -r requirements.txt
    python build_all.py              # STL into ../stl and previews into ../docs/img
    python build_all.py --no-preview # STL only
"""
import argparse
import itertools
import sys
from pathlib import Path

import trimesh
from build123d import Pos, Rot, export_stl

import cage as C
import parts as K
import params as P

ROOT = Path(__file__).resolve().parent.parent
STL_DIR = ROOT / "stl"
IMG_DIR = ROOT / "docs" / "img"


def to_bed(shape):
    """Centre on X/Y and drop onto Z = 0."""
    bb = shape.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * shape


def print_parts():
    """Each part in its print orientation (no support needed)."""
    return {
        "tray": to_bed(K.tray()),                       # floor on the bed
        "platform": to_bed(K.platform()),               # top side up
        "wheel": to_bed(Rot(X=90) * K.wheel()),         # front face on the bed
        "wheel_cap": to_bed(Rot(X=-90) * K.cap()),      # flange on the bed
        "dupont_cover": to_bed(Rot(X=180) * K.cover()), # roof on the bed
        "cage_net": to_bed(C.net()),                    # flat net, outer faces on the bed
        "esp_fit_test": to_bed(K.esp_fit_test()),       # optional: the ESP32 pocket alone
    }


def assembly_parts():
    return {
        "tray": K.tray(press=False),            # the ESP32 friction fit overlaps the board on purpose
        "platform": K.platform(grip=False),     # the friction ribs overlap the tray on purpose
        "wheel": K.place_wheel(K.wheel()),
        "wheel_cap": K.place_wheel(K.cap(grip=False)),   # its friction ribs overlap the wheel on purpose
        "dupont_cover": K.place_wheel(K.cover()),
        "cage": C.folded(),
    }


def overlap(a, b):
    try:
        return abs((a & b).volume)
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-preview", action="store_true")
    args = ap.parse_args()
    STL_DIR.mkdir(exist_ok=True)

    ok = True
    print("Printable parts")
    for name, shape in print_parts().items():
        path = STL_DIR / f"{name}.stl"
        export_stl(shape, str(path), tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load(path)
        # the net is one body when the hinges are on, several panels otherwise
        one_body = name != "cage_net" or P.HINGES
        bad = not (m.is_watertight and m.is_winding_consistent
                   and (not one_body or len(m.split(only_watertight=False)) == 1))
        ok &= not bad
        e = m.extents
        print(f"  {name:12s} {e[0]:6.1f} x {e[1]:6.1f} x {e[2]:6.1f} mm  "
              f"{abs(m.volume) / 1000:6.1f} cm3  {'WATERTIGHT' if not bad else 'PROBLEM'}")

    print("Interference check (assembled, should all be ~0 mm3)")
    asm = assembly_parts()
    ghosts = {"esp32": K.esp32_ghost(), "display": K.place_wheel(K.lcd_ghost())}
    for (na, a), (nb, b) in itertools.combinations({**asm, **ghosts}.items(), 2):
        if na in ghosts and nb in ghosts:
            continue
        v = overlap(a, b)
        if v > 0.5:
            ok = False
            print(f"  OVERLAP {na} / {nb}: {v:.1f} mm3")
    print("  done")

    if not args.no_preview:
        import render
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        render.make_previews(asm, ghosts, print_parts(), IMG_DIR)
        print(f"Previews written to {IMG_DIR}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()


