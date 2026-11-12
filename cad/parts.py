"""Parametric parts of the hamster wheel desk toy (build123d): tray, lid, wheel, cap.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Every builder returns a solid in ASSEMBLY coordinates:
  X = left/right, Y = front (negative, toward the viewer) to back, Z = up,
  origin = centre of the tray footprint, Z = 0 on the table.
build_all.py reorients each part for printing. The cage lives in cage.py.
"""
from math import hypot

from build123d import Align, Box, Cone, Cylinder, Location, Plane, Polygon, Pos, Rot, extrude

import params as P

MIN = (Align.MIN, Align.MIN, Align.MIN)
CEN = (Align.CENTER, Align.CENTER, Align.MIN)
SQ = 2 - 2 ** 0.5   # change of a 45 degree chamfer per mm of outline offset

# ------------------------------------------------------------ derived values
RIB_H = P.ESP_PIN_LEN + 0.5                       # the board sits on a central rib
BOARD_TOP = P.FLOOR + RIB_H + P.ESP_PCB_T         # top face of the ESP32 PCB
TRAY_H = BOARD_TOP + P.ESP_TOP_H + P.WIRE_ROOM + P.LID_T
SEAT_Z = TRAY_H - P.LID_T                         # underside of the lid
INNER_L = P.TRAY_L - 2 * P.WALL
INNER_W = P.TRAY_W - 2 * P.WALL
BOARD_X1 = INNER_L / 2 - 1.2                      # USB end of the board (right)
BOARD_X0 = BOARD_X1 - P.ESP_L

# wheel housing depth: tunnel + glass + pcb + rear space
Y_GLASS = P.WHEEL_TUBE
Y_PCB = Y_GLASS + P.LCD_GLASS_T
Y_BACK = Y_PCB + P.LCD_PCB_T                      # back face of the PCB
WHEEL_DEPTH = Y_BACK + P.LCD_REAR_SPACE
H_CENTER = P.FOOT_H + P.WHEEL_D / 2               # ring axis height above the foot base
WHEEL_H = P.FOOT_H + P.WHEEL_D
POCKET_D = 1.2                                    # depth of the foot seat in the lid
WHEEL_Z = TRAY_H - POCKET_D                       # assembly Z of the foot base
CHAN_W = 20.0                                     # wire channel width in the foot
TAIL_W = 24.0                                     # cap tail width over the channel

# Lid rim: two thin walls with a groove between them, the cage walls plug into it.
# Offsets are distances inward from the tray outline.
LID_OFF = P.WALL - P.SEAT_W + P.LID_FIT           # outer face of the lid
GROOVE_W = P.CAGE_T + 2 * P.CAGE_FIT              # groove width
CAGE_OFF = LID_OFF + P.LID_RIM_W + P.CAGE_FIT     # outer face of the cage walls
GROOVE_IN_OFF = LID_OFF + P.LID_RIM_W + GROOVE_W  # inner face of the groove (outer face of the inner wall)
RIM_IN_OFF = GROOVE_IN_OFF + P.LID_RIM_W          # inner face of the inner wall
OUTER_WALL_H = P.LID_BORDER_H - 2.0               # lower outer wall: easier to guide the cage in


# ------------------------------------------------------------------ helpers
def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_y(d, y0, y1, x=0.0, z=0.0):
    """Cylinder with its axis along +Y, from y0 to y1."""
    return Pos(x, y0, z) * (Rot(X=-90) * Cylinder(d / 2, y1 - y0, align=CEN))


def fuse_all(shapes):
    shapes = list(shapes)
    return shapes[0].fuse(*shapes[1:]).clean()


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
    t -= prism(outline(-P.WALL), P.FLOOR, TRAY_H + 1)
    # seat for the lid: the opening widens by SEAT_W in the top LID_T millimetres
    t -= prism(outline(-(P.WALL - P.SEAT_W)), SEAT_Z, TRAY_H + 1)

    # ESP32 lies lengthwise along X, right under the wheel: central rib under the
    # PCB (headers hang on both sides of it), low guides on the long sides and a
    # stop at the far end. USB-C points to the right wall.
    yc = P.BOARD_Y
    rz = P.FLOOR - 0.1
    gz = P.FLOOR + RIB_H + P.ESP_PCB_T + 1.5
    t += box(BOARD_X0 + 3, BOARD_X1 - 8, yc - 8, yc + 8, rz, P.FLOOR + RIB_H)
    g_in = P.ESP_W / 2 + 0.4
    for s in (-1, 1):
        a, b = sorted((yc + s * g_in, yc + s * (g_in + 1.2)))
        t += box(BOARD_X0 + 3, BOARD_X1 - 8, a, b, rz, gz)
    t += box(BOARD_X0 - 1.6, BOARD_X0 - 0.4, yc - g_in - 1.2, yc + g_in + 1.2, rz, gz)

    # USB-C opening in the right wall, centred on the board
    zc = BOARD_TOP + P.USB_AXIS_ABOVE_PCB
    t -= box(INNER_L / 2 - 1, P.TRAY_L / 2 + 1, yc - P.USB_HOLE_W / 2, yc + P.USB_HOLE_W / 2,
             zc - P.USB_HOLE_H / 2, zc + P.USB_HOLE_H / 2)
    return t


# ---------------------------------------------------------------------- lid
def lid():
    plate = prism(outline(-LID_OFF), SEAT_Z, TRAY_H)
    # rim: a low outer wall and a tall inner wall, with the cage groove between them
    outer = prism(outline(-LID_OFF), TRAY_H, TRAY_H + OUTER_WALL_H) \
        - prism(outline(-LID_OFF - P.LID_RIM_W), TRAY_H - 1, TRAY_H + OUTER_WALL_H + 1)
    inner = prism(outline(-GROOVE_IN_OFF), TRAY_H, TRAY_H + P.LID_BORDER_H) \
        - prism(outline(-RIM_IN_OFF), TRAY_H - 1, TRAY_H + P.LID_BORDER_H + 1)
    lid_ = plate + outer + inner

    # one dimple per wall, where the snap bump of the cage clicks in
    pts = outline(-GROOVE_IN_OFF)
    for (mx, my), (tx, ty), (nx, ny), ln in edges(pts):
        if ln > 8:
            pl = Plane(origin=(mx, my, TRAY_H + 2.5), x_dir=(tx, ty, 0), z_dir=(-nx, -ny, 0))
            lid_ -= Location(pl) * (Pos(0, 0, -0.1) * Cone(
                P.BUMP_R + 0.4, P.BUMP_R - 0.1, P.DIMPLE_D + 0.1, align=CEN))

    # seat for the wheel foot and slot for the wires
    x0 = P.WHEEL_X - P.FOOT_W / 2 - 0.25
    x1 = P.WHEEL_X + P.FOOT_W / 2 + 0.25
    y0 = P.WHEEL_Y - 0.25
    y1 = P.WHEEL_Y + WHEEL_DEPTH + P.CAP_T + 0.25
    pocket = box(x0, x1, y0, y1, TRAY_H - POCKET_D, TRAY_H + 1)
    if abs((pocket & inner).volume) > 0.1:
        raise ValueError("the wheel foot does not fit inside the lid rim: "
                         "increase TRAY_L / TRAY_W or move the wheel (WHEEL_X, WHEEL_Y)")
    lid_ -= pocket
    lid_ -= box(P.WHEEL_X - CHAN_W / 2 - 1, P.WHEEL_X + CHAN_W / 2 + 1,
                P.WHEEL_Y + Y_BACK - 0.5, P.WHEEL_Y + WHEEL_DEPTH + P.CAP_T,
                SEAT_Z - 1, TRAY_H + 1)
    return lid_


# -------------------------------------------------------------------- wheel
def _foot_prism():
    """Trapezoid foot, extruded along +Y over the full housing depth."""
    fw = P.FOOT_W / 2
    top = P.WHEEL_D / 2 * 0.8
    prof = Plane.XZ * Polygon((-fw, 0), (fw, 0), (top, H_CENTER), (-top, H_CENTER), align=None)
    return extrude(prof, amount=-WHEEL_DEPTH)


def wheel():
    """Ring housing and foot, in WHEEL coordinates (X centred, Y front=0, Z base=0)."""
    body = cyl_y(P.WHEEL_D, 0, WHEEL_DEPTH, z=H_CENTER) + _foot_prism()
    # window, glass seat, PCB seat
    body -= cyl_y(P.WHEEL_WINDOW_D, -1, Y_GLASS + 1, z=H_CENTER)
    body -= Pos(0, 0, H_CENTER) * (Rot(X=-90) * Cone(
        P.WHEEL_WINDOW_D / 2 + P.WHEEL_FLARE, P.WHEEL_WINDOW_D / 2, P.WHEEL_FLARE, align=CEN))
    body -= cyl_y(P.LCD_GLASS_D + 2 * P.FIT, Y_GLASS, Y_PCB + 0.01, z=H_CENTER)
    body -= cyl_y(P.LCD_PCB_D + 2 * P.FIT, Y_PCB, WHEEL_DEPTH + 1, z=H_CENTER)
    # wire channel from the PCB pocket down through the foot (open at the back)
    body -= box(-CHAN_W / 2, CHAN_W / 2, Y_BACK, WHEEL_DEPTH + 1, -1, H_CENTER - 12)
    if P.CAP_SCREWS:
        r = (P.WHEEL_D / 2 + (P.LCD_PCB_D / 2 + P.FIT)) / 2
        for s in (-1, 1):
            body -= cyl_y(1.7, WHEEL_DEPTH - 8, WHEEL_DEPTH + 1, x=s * r, z=H_CENTER)
    return body


def cap():
    """Rear cap in WHEEL coordinates: flange at the back, boss pressing on the PCB."""
    zc = H_CENTER
    flange = cyl_y(P.WHEEL_D, WHEEL_DEPTH, WHEEL_DEPTH + P.CAP_T, z=zc)
    tail = box(-TAIL_W / 2, TAIL_W / 2, WHEEL_DEPTH, WHEEL_DEPTH + P.CAP_T, 0, zc)
    boss = cyl_y(P.LCD_PCB_D + 2 * P.FIT - 2 * P.CAP_PRESS, Y_BACK, WHEEL_DEPTH, z=zc)
    boss -= cyl_y(P.LCD_PCB_D - 8, Y_BACK - 1, WHEEL_DEPTH + 1, z=zc)
    # notch for the display header pins and wires at the bottom of the boss
    boss -= box(-P.LCD_PIN_SLOT_W / 2, P.LCD_PIN_SLOT_W / 2, Y_BACK - 1, WHEEL_DEPTH + 1,
                zc - P.LCD_PCB_D / 2 - 1, zc - P.LCD_PCB_D / 2 + 9)
    c = flange + tail + boss
    if P.CAP_SCREWS:
        r = (P.WHEEL_D / 2 + (P.LCD_PCB_D / 2 + P.FIT)) / 2
        for s in (-1, 1):
            c -= cyl_y(2.4, WHEEL_DEPTH - 1, WHEEL_DEPTH + P.CAP_T + 1, x=s * r, z=zc)
    return c


def place_wheel(shape):
    """Move a wheel-frame part to its assembly position."""
    return Pos(P.WHEEL_X, P.WHEEL_Y, WHEEL_Z) * shape


# ---------------------------------------------------------- reference models
def esp32_ghost():
    """Dummy ESP32 board, only used for fit checks and previews."""
    yc = P.BOARD_Y
    b = box(BOARD_X0, BOARD_X1, yc - P.ESP_W / 2, yc + P.ESP_W / 2, BOARD_TOP - P.ESP_PCB_T, BOARD_TOP)
    b += box(BOARD_X1 - 4, BOARD_X1 + 1.0, yc - 4.5, yc + 4.5, BOARD_TOP, BOARD_TOP + 3.3)
    b += box(BOARD_X0 + 2, BOARD_X0 + 27, yc - 9, yc + 9, BOARD_TOP, BOARD_TOP + 3.3)
    for s in (-1, 1):  # header pins below the board
        y = yc + s * 11.43
        b += box(BOARD_X0 + 2, BOARD_X1 - 2, y - 1.3, y + 1.3,
                 BOARD_TOP - P.ESP_PCB_T - P.ESP_PIN_LEN, BOARD_TOP - P.ESP_PCB_T)
    return b


def lcd_ghost():
    """Dummy GC9A01 module in wheel coordinates (for fit checks)."""
    zc = H_CENTER
    pcb = cyl_y(P.LCD_PCB_D, Y_PCB, Y_BACK, z=zc)
    glass = cyl_y(P.LCD_GLASS_D, Y_GLASS, Y_PCB, z=zc)
    header = box(-8.9, 8.9, Y_BACK, Y_BACK + 2.5, zc - P.LCD_PCB_D / 2 + 1, zc - P.LCD_PCB_D / 2 + 3.5)
    return pcb + glass + header

