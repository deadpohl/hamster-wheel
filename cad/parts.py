"""Parametric parts of the hamster wheel desk toy (build123d): tray, lid, wheel, cap, cover.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Every builder returns a solid in ASSEMBLY coordinates unless noted:
  X = left/right, Y = front (negative, toward the viewer) to back, Z = up,
  origin = centre of the tray footprint, Z = 0 on the table.
build_all.py reorients each part for printing. The cage lives in cage.py.

How the wiring is laid out (plain Dupont jumper wires, no soldering):
  * the ESP32 lies upside down in the front half of the tray, pins up, resting on its
    module and USB-C socket. Its antenna slides under a bridge, the USB end clicks
    under a flexible bar. The tray is deep enough for the Dupont connectors and the
    wires to stay inside;
  * the display connectors point straight back from the tab of the PCB, into a bay in
    the foot of the wheel. The wires go down through a hole in the lid, behind the
    ESP32, and a cover hides the bay.
"""
from math import hypot

from build123d import Align, Box, Cone, Cylinder, Location, Plane, Polygon, Pos, Rot, extrude

import params as P

MIN = (Align.MIN, Align.MIN, Align.MIN)
CEN = (Align.CENTER, Align.CENTER, Align.MIN)
SQ = 2 - 2 ** 0.5   # change of a 45 degree chamfer per mm of outline offset

# ------------------------------------------------------------ derived values
BOARD_BOT = P.FLOOR + P.ESP_UNDER_H               # underside of the ESP32 PCB (it faces down)
BOARD_TOP = BOARD_BOT + P.ESP_PCB_T               # pin side of the PCB
SEAT_Z = BOARD_TOP + P.DUPONT_H + P.WIRE_BEND     # underside of the lid
TRAY_H = SEAT_Z + P.LID_T
INNER_L = P.TRAY_L - 2 * P.WALL
INNER_W = P.TRAY_W - 2 * P.WALL
# USB end of the PCB (left): room for the USB-C socket nose and for the flexible bar
BOARD_X0 = -INNER_L / 2 + max(2.7, P.USB_NOSE + 0.3)
BOARD_X1 = BOARD_X0 + P.ESP_L                     # antenna end (right), the antenna sticks out further
BOARD_YC = P.BOARD_Y
ROW_DY = 12.7                                     # pin rows, from the board centre line (25.4 apart)

# wheel housing: tunnel, glass, PCB, then the bay for the Dupont connectors
Y_GLASS = P.WHEEL_TUBE
Y_PCB = Y_GLASS + P.LCD_GLASS_T
Y_BACK = Y_PCB + P.LCD_PCB_T                      # back face of the display PCB
WHEEL_DEPTH = Y_BACK + P.LCD_REAR_SPACE           # ring and foot depth
H_CENTER = P.FOOT_H + P.WHEEL_D / 2               # ring axis height above the foot base
WHEEL_H = P.FOOT_H + P.WHEEL_D
TAB_BOT = H_CENTER + P.LCD_PCB_D / 2 - P.LCD_H_TOTAL   # bottom edge of the display tab
PIN_Z = TAB_BOT + P.LCD_PIN_Z                     # display pin row
if TAB_BOT < 1.5:
    raise ValueError("the display tab goes below the foot of the wheel: increase FOOT_H")
POCKET_D = 1.2                                    # depth of the foot seat in the lid
WHEEL_Z = TRAY_H - POCKET_D                       # assembly Z of the foot base
BAY_TOP = PIN_Z + 1.27 + 3.0                      # height of the bay in the foot
COVER_Y0 = WHEEL_DEPTH + P.CAP_T
COVER_Y1 = Y_BACK + P.LCD_CONN_LEN + P.WIRE_BEND_LCD
COVER_HW = P.BAY_W / 2 + P.COVER_WALL             # half width of the cover (outside)
WHEEL_X = P.WHEEL_X

# Lid rim: two thin walls with a groove between them, the cage walls plug into it.
# Offsets are distances inward from the tray outline.
LID_OFF = P.WALL - P.SEAT_W + P.LID_FIT           # outer face of the lid
GROOVE_W = P.CAGE_T + 2 * P.CAGE_FIT              # groove width
CAGE_OFF = LID_OFF + P.LID_RIM_W + P.CAGE_FIT     # outer face of the cage walls
GROOVE_IN_OFF = LID_OFF + P.LID_RIM_W + GROOVE_W  # inner face of the groove (outer face of the inner wall)
RIM_IN_OFF = GROOVE_IN_OFF + P.LID_RIM_W          # inner face of the inner wall
OUTER_WALL_H = P.LID_BORDER_H - 2.0               # lower outer wall: easier to guide the cage in
# the wheel stands as far back as the rim allows, so the wire hole is behind the ESP32
WHEEL_Y = P.TRAY_W / 2 - RIM_IN_OFF - 0.6 - (COVER_Y1 + P.COVER_WALL + 0.25)


# ------------------------------------------------------------------ helpers
def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_y(d, y0, y1, x=0.0, z=0.0):
    """Cylinder with its axis along +Y, from y0 to y1."""
    return Pos(x, y0, z) * (Rot(X=-90) * Cylinder(d / 2, y1 - y0, align=CEN))


def fuse_all(shapes):
    shapes = list(shapes)
    return shapes[0].fuse(*shapes[1:]).clean()


def vol(shape):
    try:
        return abs(shape.volume)
    except Exception:
        return 0.0


def oct_pts(a, b, c):
    """Clockwise outline of a rectangle (half sizes a, b) with its corners cut by c."""
    if c < 0.01:
        return [(-a, b), (a, b), (a, -b), (-a, -b)]
    return [(-(a - c), b), (a - c, b), (a, b - c), (a, -(b - c)), (a - c, -b), (-(a - c), -b),
            (-a, -(b - c)), (-a, b - c)]


def outline(d=0.0):
    """Tray outline offset by d mm (positive = outward), as clockwise points."""
    c = max(0.0, P.CORNER_CUT + SQ * d) if P.CORNER_CUT > 0 else 0.0
    return oct_pts(P.TRAY_L / 2 + d, P.TRAY_W / 2 + d, c)


def prism(pts, z0, z1):
    # both=True: the extrusion is symmetric, so the winding order of pts does not matter
    return Pos(0, 0, (z0 + z1) / 2) * extrude(Polygon(*pts, align=None), amount=(z1 - z0) / 2, both=True)


def edges(pts):
    """Yield (midpoint, unit tangent, outward normal, length) of each edge of a clockwise polygon."""
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        ln = hypot(q[0] - p[0], q[1] - p[1])
        tx, ty = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
        yield ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), (tx, ty), (-ty, tx), ln


# --------------------------------------------------------------------- tray
def tray():
    t = prism(outline(0), 0, TRAY_H)
    cavity = prism(outline(-P.WALL), P.FLOOR, TRAY_H + 1)
    t -= cavity
    # seat for the lid: the opening widens by SEAT_W in the top LID_T millimetres
    t -= prism(outline(-(P.WALL - P.SEAT_W)), SEAT_Z, TRAY_H + 1)

    # ESP32 upside down, resting on its module and USB-C socket. Nothing clamps the long
    # edges: the header plastic covers them. It is held at both ends instead.
    yc, x0, x1 = BOARD_YC, BOARD_X0, BOARD_X1
    hw = P.ESP_W / 2
    zb, zt = BOARD_BOT, BOARD_TOP
    fz = P.FLOOR - 0.1
    feats = []
    # side guides just outside the long edges, lower than the PCB top
    for s in (-1, 1):
        a, b = yc + s * (hw + 0.3), yc + s * (hw + 1.5)
        feats.append(box(x0 + 4, x1 - 4, min(a, b), max(a, b), fz, zt - 0.3))

    # antenna end: a bridge over the antenna, the board slides under it
    ah = P.ESP_ANT_W / 2 + 1.5                 # half width of the opening (modules are not always centred)
    xa0, xa1 = x1 + 2.0, x1 + P.ESP_ANT_L + 0.8
    roof_z = zb + 0.25                          # the antenna top is level with the PCB underside
    feats.append(box(xa0, xa1 + 1.5, yc - ah - 2.0, yc + ah + 2.0, fz, roof_z + 1.6))

    # USB end: a thin bar across the end of the board, held by a post at each end. It bends
    # toward the wall when the board is pressed down, then its lip snaps over the PCB.
    bx0, bx1 = x0 - 1.7, x0 - 0.7               # 1 mm thick, 1 mm free toward the wall
    lip_z = zt + 0.2
    bz1 = lip_z + 1.2
    for s in (-1, 1):
        a, b = yc + s * 13.0, yc + s * (hw + 1.5)
        feats.append(box(bx0, bx1, min(a, b), max(a, b), fz, bz1))
    feats.append(box(bx0, bx1, yc - 13.0, yc + 13.0, zb + 0.3, bz1))   # above the USB-C socket
    lip = [(bx1 - 0.1, lip_z), (x0 + 0.6, lip_z), (x0 + 0.6, lip_z + 0.3), (bx1 - 0.1, bz1)]
    feats.append(Pos(0, yc, 0) * extrude(Plane.XZ * Polygon(*lip, align=None), amount=6.0, both=True))

    keep = prism(outline(-P.WALL + 0.5), 0, TRAY_H)   # features may merge into the walls, never stick out
    t += fuse_all(feats) & keep
    t -= box(xa0 - 1, xa1, yc - ah, yc + ah, P.FLOOR, roof_z)          # the opening under the bridge
    # pockets under the EN and BOOT buttons, so they can never be pressed by the floor
    for s in (-1, 1):
        a, b = yc + s * 5.0, yc + s * 11.5
        t -= box(x0 - 0.2, x0 + 7.5, min(a, b), max(a, b), P.FLOOR - 1.2, P.FLOOR + 0.1)

    # USB-C opening in the left wall, open at the bottom: the plug body is taller than the
    # socket and reaches below the floor level
    t -= box(-P.TRAY_L / 2 - 1, -INNER_L / 2 + 0.5, yc - P.USB_HOLE_W / 2, yc + P.USB_HOLE_W / 2,
             -1, zt + 2.5)
    return t


# ---------------------------------------------------------------------- lid
def lid():
    plate = prism(outline(-LID_OFF), SEAT_Z, TRAY_H)
    # rim: a low outer wall and a tall inner wall, with the cage groove between them
    c = P.LEAD_IN
    outer = prism(outline(-LID_OFF), TRAY_H, TRAY_H + OUTER_WALL_H) \
        - prism(outline(-LID_OFF - P.LID_RIM_W), TRAY_H - 1, TRAY_H + OUTER_WALL_H + 1)
    # lead-in: the groove side of each wall is chamfered at the top, so the mouth is wider
    outer -= Pos(0, 0, TRAY_H + OUTER_WALL_H - c) * extrude(
        Polygon(*outline(-LID_OFF - P.LID_RIM_W)[::-1], align=None), amount=c + 0.01, taper=-45)
    inner = prism(outline(-GROOVE_IN_OFF), TRAY_H, TRAY_H + P.LID_BORDER_H - c) \
        + Pos(0, 0, TRAY_H + P.LID_BORDER_H - c) * extrude(
            Polygon(*outline(-GROOVE_IN_OFF)[::-1], align=None), amount=c, taper=45)
    inner -= prism(outline(-RIM_IN_OFF), TRAY_H - 1, TRAY_H + P.LID_BORDER_H + 1)
    lid_ = plate + outer + inner

    # one dimple per wall, where the snap bump of the cage clicks in
    pts = outline(-GROOVE_IN_OFF)
    for (mx, my), (tx, ty), (nx, ny), ln in edges(pts):
        if ln > 10:
            pl = Plane(origin=(mx, my, TRAY_H + 2.5), x_dir=(tx, ty, 0), z_dir=(-nx, -ny, 0))
            lid_ -= Location(pl) * (Pos(0, 0, -0.1) * Cone(
                P.BUMP_R + 0.6, P.BUMP_R + 0.1, P.DIMPLE_D + 0.2, align=CEN))

    # seats for the wheel foot and for the connector cover
    pz0 = TRAY_H - POCKET_D
    foot = box(WHEEL_X - P.FOOT_W / 2 - 0.25, WHEEL_X + P.FOOT_W / 2 + 0.25,
               WHEEL_Y - 0.25, WHEEL_Y + WHEEL_DEPTH + P.CAP_T + 0.25, pz0, TRAY_H + 1)
    cover = box(WHEEL_X - COVER_HW - 0.25, WHEEL_X + COVER_HW + 0.25,
                WHEEL_Y + COVER_Y0 - 0.25, WHEEL_Y + COVER_Y1 + P.COVER_WALL + 0.25, pz0, TRAY_H + 1)
    if vol((foot + cover) & inner) > 0.1:
        raise ValueError("the wheel does not fit inside the lid rim: increase TRAY_L / TRAY_W "
                         "or move the ESP32 (BOARD_Y)")
    lid_ -= foot + cover
    # wire hole under the bay and the cover, behind the ESP32: big enough to pass the
    # Dupont connectors one by one
    lid_ -= box(WHEEL_X - P.BAY_W / 2 + 2, WHEEL_X + P.BAY_W / 2 - 2, WHEEL_Y + Y_BACK + 0.5,
                WHEEL_Y + COVER_Y1 - 0.5, SEAT_Z - 1, TRAY_H + 1)
    return lid_


# -------------------------------------------------------------------- wheel
def _foot_prism():
    """Trapezoid foot, extruded along +Y over the full housing depth."""
    fw = P.FOOT_W / 2
    top = P.WHEEL_D / 2 * 0.8
    prof = Plane.XZ * Polygon((-fw, 0), (fw, 0), (top, H_CENTER), (-top, H_CENTER), align=None)
    return extrude(prof, amount=-WHEEL_DEPTH)


def _screw_r():
    return (P.WHEEL_D / 2 + (P.LCD_PCB_D / 2 + P.FIT)) / 2


def wheel():
    """Ring housing and foot, in WHEEL coordinates (X centred, Y front=0, Z base=0)."""
    body = cyl_y(P.WHEEL_D, 0, WHEEL_DEPTH, z=H_CENTER) + _foot_prism()
    # window, glass seat, PCB seat
    body -= cyl_y(P.WHEEL_WINDOW_D, -1, Y_GLASS + 1, z=H_CENTER)
    body -= Pos(0, 0, H_CENTER) * (Rot(X=-90) * Cone(
        P.WHEEL_WINDOW_D / 2 + P.WHEEL_FLARE, P.WHEEL_WINDOW_D / 2, P.WHEEL_FLARE, align=CEN))
    body -= cyl_y(P.LCD_GLASS_D + 2 * P.FIT, Y_GLASS, Y_PCB + 0.01, z=H_CENTER)
    body -= cyl_y(P.LCD_PCB_D + 2 * P.FIT, Y_PCB, WHEEL_DEPTH + 1, z=H_CENTER)
    # the tab at the bottom of the display PCB (1 mm deeper at the front for the parts on it)
    tw = P.LCD_TAB_W / 2 + P.FIT
    body -= box(-tw, tw, Y_PCB - 1.0, WHEEL_DEPTH + 1, TAB_BOT - 0.5, H_CENTER)
    # bay behind the PCB: the Dupont connectors point straight back, the wires go down
    body -= box(-P.BAY_W / 2, P.BAY_W / 2, Y_BACK, WHEEL_DEPTH + 1, -1, BAY_TOP)
    if P.CAP_SCREWS:
        for s in (-1, 1):
            body -= cyl_y(1.7, WHEEL_DEPTH - 8, WHEEL_DEPTH + 1, x=s * _screw_r(), z=H_CENTER)
    return body


def cap():
    """Rear cap in WHEEL coordinates: flange at the back, boss pressing on the PCB."""
    zc = H_CENTER
    flange = cyl_y(P.WHEEL_D, WHEEL_DEPTH, WHEEL_DEPTH + P.CAP_T, z=zc)
    boss = cyl_y(P.LCD_PCB_D + 2 * P.FIT - 2 * P.CAP_PRESS, Y_BACK, WHEEL_DEPTH, z=zc)
    boss -= cyl_y(P.LCD_PCB_D - 8, Y_BACK - 1, WHEEL_DEPTH + 1, z=zc)
    c = flange + boss
    # the connectors go through here: a U shaped notch open at the bottom of the cap,
    # the boss only presses on the round part of the PCB
    c -= box(-P.BAY_W / 2 + 4, P.BAY_W / 2 - 4, Y_BACK - 1, WHEEL_DEPTH + P.CAP_T + 1,
             -1, max(BAY_TOP, H_CENTER - P.LCD_PCB_D / 2 + 3.0))
    if P.CAP_SCREWS:
        for s in (-1, 1):
            c -= cyl_y(2.4, WHEEL_DEPTH - 1, WHEEL_DEPTH + P.CAP_T + 1, x=s * _screw_r(), z=zc)
    return c


def wheel_cover():
    """Cover over the connector bay and the lid slot, in WHEEL coordinates (open at the front and bottom)."""
    w = P.COVER_WALL
    c = box(-COVER_HW, COVER_HW, COVER_Y0, COVER_Y1 + w, 0, P.COVER_H + w)
    c -= box(-P.BAY_W / 2, P.BAY_W / 2, COVER_Y0 - 1, COVER_Y1, -1, P.COVER_H)
    return c


def place_wheel(shape):
    """Move a wheel-frame part to its assembly position."""
    return Pos(WHEEL_X, WHEEL_Y, WHEEL_Z) * shape


# ---------------------------------------------------------- reference models
def esp32_ghost():
    """Dummy ESP32 board (upside down) with its Dupont connectors, for fit checks and previews."""
    yc, x0, x1 = BOARD_YC, BOARD_X0, BOARD_X1
    hw = P.ESP_W / 2
    zb, zt = BOARD_BOT, BOARD_TOP
    fl = P.FLOOR + 0.05
    b = box(x0, x1, yc - hw, yc + hw, zb, zt)
    # underside: module (its antenna sticks out past the PCB), USB-C socket and buttons
    b += box(x1 - 19.0, x1, yc - 9, yc + 9, fl, zb)
    aw = P.ESP_ANT_W / 2
    b += box(x1, x1 + P.ESP_ANT_L, yc - aw, yc + aw, zb - 0.9, zb)
    b += box(x0 - P.USB_NOSE, x0 + 7.0, yc - 4.5, yc + 4.5, fl, zb)
    for s in (-1, 1):
        a, c = yc + s * 6.5, yc + s * 10.3
        b += box(x0 + 0.5, x0 + 5.5, min(a, c), max(a, c), fl, zb)
    # pin headers (19 pins, a little longer than the PCB), then the Dupont connectors on
    # the pins in use: GPIO 23 to 16 on the back row, 3V3 at the antenna end of the front row
    for s in (-1, 1):
        y = yc + s * ROW_DY
        b += box(x0 - 0.6, x1 + 0.6, y - 1.27, y + 1.27, zt, zt + P.ESP_HDR_H)
    xk = lambda k: x1 - 0.7 - (k - 1) * 2.54
    top = zt + P.DUPONT_H
    b += box(xk(11) - 1.27, xk(1) + 1.27, yc + ROW_DY - 1.27, yc + ROW_DY + 1.27, zt, top)
    b += box(xk(1) - 1.27, xk(1) + 1.27, yc - ROW_DY - 1.27, yc - ROW_DY + 1.27, zt, top)
    return b


def lcd_ghost():
    """Dummy GC9A01 module with its 7 Dupont connectors, in wheel coordinates."""
    zc = H_CENTER
    pcb = cyl_y(P.LCD_PCB_D, Y_PCB, Y_BACK, z=zc)
    pcb += box(-P.LCD_TAB_W / 2, P.LCD_TAB_W / 2, Y_PCB, Y_BACK, TAB_BOT, zc)
    glass = cyl_y(P.LCD_GLASS_D, Y_GLASS, Y_PCB, z=zc)
    conn = box(-8.9, 8.9, Y_BACK, Y_BACK + P.LCD_CONN_LEN, PIN_Z - 1.27, PIN_Z + 1.27)
    return pcb + glass + conn

