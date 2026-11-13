"""The cage: printed flat as one net, folded into a cage that plugs into the lid.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

The net is a roof in the middle with one wall panel around each of its edges,
joined by thin living hinges. Everything is printed with the OUTER faces on the
bed (no supports). Fold the walls up 90 degrees and push their solid skirts into
the groove that runs around the rim of the lid: the groove holds every panel in
place, so the mitred corners close without glue, and a small bump on each wall
clicks into a dimple of the lid rim.

Panel frame (used for the flat net and for the folded cage):
  X = along the edge, Y = h, distance from the roof (0 at the top, HW at the skirt),
  Z = w, thickness from the OUTER face (0) to the inner face (CAGE_T).
"""
from math import atan2, degrees, hypot, tan, radians

from build123d import Align, Cone, Location, Plane, Polygon, Pos, Rot, extrude

import params as P
import parts as K
from parts import box, edges, fuse_all, outline, prism

T = P.CAGE_T
CAGE_TOP = K.WHEEL_Z + K.WHEEL_H + P.ROOF_GAP + T   # Z of the outer face of the roof
HW = CAGE_TOP - K.TRAY_H                     # wall height: roof to the bottom of the skirt (groove floor)
FILM = P.HINGE_FILM


def _fuse(shapes):
    shapes = list(shapes)
    return shapes[0] if len(shapes) == 1 else fuse_all(shapes)


def _vertex_angle(pts):
    """Exterior angle (degrees) at the vertices: 90 for a rectangle, 45 for a chamfered one."""
    (ax, ay), (bx, by), (cx, cy) = pts[0], pts[1], pts[2]
    a1 = atan2(by - ay, bx - ax)
    a2 = atan2(cy - by, cx - bx)
    return abs(degrees(a2 - a1)) % 180


def _spread(half, pitch):
    """Interior bar positions between -half and +half (ends are solid posts/rails)."""
    n = max(1, round(2 * half / pitch))
    return [-half + i * 2 * half / n for i in range(1, n)]


# ----------------------------------------------------------------- roof
def roof():
    r_pts = outline(-K.CAGE_OFF)
    # full thickness at the hinge film, then a 45 degree bevel on the inner face so
    # that the mitre closes when the wall is folded
    plate = prism(r_pts, 0, FILM) + Pos(0, 0, FILM) * extrude(
        Polygon(*r_pts[::-1], align=None), amount=T - FILM, taper=45)
    win_pts = outline(-K.CAGE_OFF - P.RAIL_W)
    xs = [p[0] for p in win_pts]
    ys = [p[1] for p in win_pts]
    ax, ay = max(xs), max(ys)
    bars = [box(x - P.BAR_W / 2, x + P.BAR_W / 2, -ay - 1, ay + 1, -1, T + 1) for x in _spread(ax, P.ROOF_PITCH)]
    bars += [box(-ax - 1, ax + 1, y - P.BAR_W / 2, y + P.BAR_W / 2, -1, T + 1) for y in _spread(ay, P.ROOF_PITCH)]
    hole = prism(win_pts, -1, T + 1)
    if bars:
        hole = hole - _fuse(bars)
    return plate - hole


# ----------------------------------------------------------- wall panel
def wall_panel(length, front, beta_tan):
    """One wall panel in the panel frame (see the module docstring)."""
    body = box(-length / 2, length / 2, 0, HW, 0, T)

    # open window between the posts, the top rail and the skirt
    iu = length / 2 - P.POST_W
    if iu > 2.0:
        window = box(-iu, iu, P.RAIL_W, HW - P.RIM_H, -1, T + 1)
        bars = [box(u - P.BAR_W / 2, u + P.BAR_W / 2, P.RAIL_W - 0.5, HW - P.RIM_H + 0.5, -1, T + 1)
                for u in _spread(iu, P.WALL_PITCH)]
        if not front and length > 30:       # keep the front free: the wheel must be seen
            hm = (P.RAIL_W + HW - P.RIM_H) / 2
            bars.append(box(-iu - 0.5, iu + 0.5, hm - P.BAR_W / 2, hm + P.BAR_W / 2, -1, T + 1))
        body -= window - _fuse(bars) if bars else window

    # snap bump on the inner face of the skirt (fits the groove in the tray wall)
    if length > 10:                          # same rule as the dimples of the lid
        body += Pos(0, HW - 2.5, T - 0.1) * Cone(P.BUMP_R + 0.2, P.BUMP_R - 0.2, P.BUMP_R + 0.1,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN))

    # mitre at both vertical edges: the outer face keeps the full length
    for s in (-1, 1):
        e = length / 2
        pts = [(s * (e + beta_tan), -1), (s * (e - (T + 1) * beta_tan), T + 1),
               (s * (e + 5), T + 1), (s * (e + 5), -1)]
        cut = extrude(Plane.XZ * Polygon(*pts, align=None), amount=(HW + 2) / 2, both=True)
        body -= Pos(0, HW / 2, 0) * cut

    # 45 degree bevel on the inner face at the hinge (top) end
    bev = [(-1, FILM), (0, FILM), (T + 1 - FILM, T + 1), (-1, T + 1)]
    cut = extrude(Plane.YZ * Polygon(*bev, align=None), amount=length + 2, both=True)
    body -= cut
    return body


def _panels():
    """List of (panel, edge midpoint, tangent, outward normal, length)."""
    pts = outline(-K.CAGE_OFF)
    beta_tan = tan(radians(_vertex_angle(pts) / 2))
    out = []
    for (m, t, n, ln) in edges(pts):
        front = abs(n[0]) < 0.01 and n[1] > 0.99       # becomes the front (-Y) once flipped
        out.append((wall_panel(ln, front, beta_tan), m, t, n, ln))
    return out


# ------------------------------------------------------------ outputs
def net():
    """The flat net, ready to print (outer faces on Z = 0)."""
    parts = [roof()]
    for panel, (mx, my), (tx, ty), (nx, ny), ln in _panels():
        g = P.HINGE_W
        frame = Plane(origin=(mx + g * nx, my + g * ny, 0), x_dir=(tx, ty, 0), z_dir=(0, 0, 1))
        parts.append(Location(frame) * panel)
        if P.HINGES:
            film = box(-ln / 2, ln / 2, -g - 0.3, 0.3, 0, FILM)
            parts.append(Location(frame) * film)
    return _fuse(parts)


def folded():
    """The folded cage, in assembly coordinates (roof on top, walls hanging down)."""
    parts = [roof()]
    for panel, (mx, my), (tx, ty), (nx, ny), ln in _panels():
        frame = Plane(origin=(mx, my, 0), x_dir=(tx, ty, 0), z_dir=(-nx, -ny, 0))
        parts.append(Location(frame) * panel)
    return Pos(0, 0, CAGE_TOP) * (Rot(X=180) * _fuse(parts))



