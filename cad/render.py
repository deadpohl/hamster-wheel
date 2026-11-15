"""Tiny software renderer (numpy z-buffer) used to make the README previews.

Author: DeadPohl  https://www.instagram.com/_deadpohl_
No OpenGL needed, so it also runs on a headless machine.
"""
import tempfile
from math import cos, radians, sin
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from build123d import Pos, export_stl

COLORS = {
    "tray": (205, 52, 46),
    "platform": (218, 186, 138),
    "wheel": (244, 204, 32),
    "wheel_cap": (222, 170, 22),
    "dupont_cover": (190, 150, 100),
    "cage": (118, 158, 190),
    "esp32": (30, 130, 80),
    "display": (40, 40, 48),
}


def to_mesh(shape):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "m.stl"
        export_stl(shape, str(p), tolerance=0.02, angular_tolerance=0.15)
        return trimesh.load(p)


def render(items, az=-35, el=24, size=(1100, 800), margin=0.06, ss=2):
    """items: list of (mesh, rgb). Returns a PIL image."""
    a, e = radians(az), radians(el)
    rz = np.array([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])
    right = np.array([1.0, 0, 0])
    up = np.array([0, sin(e), cos(e)])
    view = np.array([0, cos(e), -sin(e)])

    tris, cols = [], []
    for mesh, rgb in items:
        v = mesh.vertices @ rz.T
        n = mesh.face_normals @ rz.T
        sx, sy, d = v @ right, v @ up, v @ view
        pts = np.stack([sx, sy, d], axis=1)[mesh.faces]
        nc = np.stack([n @ right, n @ up, -(n @ view)], axis=1)
        light = np.array([-0.35, 0.55, 0.75]); light /= np.linalg.norm(light)
        shade = 0.38 + 0.62 * np.clip(nc @ light, 0, 1)
        tris.append(pts)
        cols.append(np.asarray(rgb)[None, :] * shade[:, None])
    tris = np.concatenate(tris)
    cols = np.concatenate(cols)

    W, H = size[0] * ss, size[1] * ss
    lo, hi = tris[:, :, :2].reshape(-1, 2).min(0), tris[:, :, :2].reshape(-1, 2).max(0)
    scale = min(W * (1 - 2 * margin) / (hi[0] - lo[0]), H * (1 - 2 * margin) / (hi[1] - lo[1]))
    ox = (W - (hi[0] - lo[0]) * scale) / 2
    oy = (H - (hi[1] - lo[1]) * scale) / 2
    px = (tris[:, :, 0] - lo[0]) * scale + ox
    py = H - ((tris[:, :, 1] - lo[1]) * scale + oy)
    pz = tris[:, :, 2]

    img = np.full((H, W, 3), 246.0)
    zbuf = np.full((H, W), np.inf)
    for i in range(len(tris)):
        x, y, z = px[i], py[i], pz[i]
        x0, x1 = int(max(np.floor(x.min()), 0)), int(min(np.ceil(x.max()), W - 1))
        y0, y1 = int(max(np.floor(y.min()), 0)), int(min(np.ceil(y.max()), H - 1))
        if x1 < x0 or y1 < y0:
            continue
        den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(den) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
        l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not inside.any():
            continue
        zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        win = inside & (zz < sub)
        sub[win] = zz[win]
        img[y0:y1 + 1, x0:x1 + 1][win] = cols[i]
    out = Image.fromarray(img.clip(0, 255).astype("uint8"))
    return out.resize(size, Image.LANCZOS) if ss > 1 else out


def make_previews(asm, ghosts, print_parts, out_dir):
    out_dir = Path(out_dir)
    meshes = {k: to_mesh(v) for k, v in asm.items()}
    gm = {k: to_mesh(v) for k, v in ghosts.items()}

    def lay(names, offsets=None, extra=()):
        items = []
        for n in names:
            m = meshes[n].copy()
            if offsets and n in offsets:
                m.apply_translation(offsets[n])
            items.append((m, COLORS[n]))
        for n in extra:
            m = gm[n].copy()
            if offsets and n in offsets:
                m.apply_translation(offsets[n])
            items.append((m, COLORS[n]))
        return items

    parts = ["tray", "platform", "wheel", "wheel_cap", "dupont_cover", "cage"]
    render(lay(parts), az=-32, el=20).save(out_dir / "assembly.jpg", quality=90)
    render(lay(parts, {"platform": (0, 0, 35), "wheel": (0, 0, 50), "wheel_cap": (0, 32, 50),
                       "dupont_cover": (0, 60, 50), "cage": (0, 0, 145)}),
           az=-32, el=22, size=(1000, 1100)).save(out_dir / "exploded.jpg", quality=90)
    render(lay(["tray"], extra=["esp32"]), az=-15, el=72, size=(1000, 760)).save(
        out_dir / "tray_inside.jpg", quality=90)
    render([(to_mesh(print_parts["cage_net"]), COLORS["cage"])], az=0, el=90, size=(1100, 950)).save(
        out_dir / "cage_net.jpg", quality=90)
    off = {"wheel_cap": (0, 30, 0), "display": (0, 14, 0)}
    render(lay(["wheel", "wheel_cap"], off, extra=["display"]), az=145, el=18, size=(1000, 760)).save(
        out_dir / "wheel_exploded.jpg", quality=90)

