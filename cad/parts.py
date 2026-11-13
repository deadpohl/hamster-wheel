"""Parametric parts of the hamster wheel desk toy (build123d): tray, lid, wheel, cap, cover.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Every builder returns a solid in ASSEMBLY coordinates unless noted:
  X = left/right, Y = front (negative, toward the viewer) to back, Z = up,
  origin = centre of the tray footprint, Z = 0 on the table.
build_all.py reorients each part for printing. The cage lives in cage.py.

How the wiring is laid out (plain Dupont jumper wires, no soldering):
  * the ESP32 lies upside down on the floor of the tray, pins up, held by four
    snap hooks. The Dupont connectors plug in from above and poke up through a big
    slot in the lid;
  * the display connectors point straight back from the PCB, into a bay in the foot
    of the wheel. A cover over the bay and the slot hides the connectors and wires.
"""
from math import hypot

from build123d import Align, Box, Cone, Cylinder, Location, Plane, Polygon, Pos, Rot, extrude

import params as P

MIN = (Align.MIN, Align.MIN, Align.MIN)
CEN = (Align.CENTER, Align.CENTER, Align.MIN)
SQ = 2 - 2 ** 0.5   # change of a 45 degree chamfer per mm of outline offset

# ------------------------------------------------------------ derived values
BOARD_BOT = P.FLOOR + P.ESP_UNDER_H + 1.0         # underside of the ESP32 PCB (it faces down)
BOARD_TOP = BOARD_BOT + P.ESP_PCB_T               # pin side of the PCB
SEAT_Z = BOARD_TOP + P.ESP_HDR_H + P.CLEAR_ABOVE  # underside of the lid
TRAY_H = SEAT_Z + P.LID_T
INNER_L = P.TRAY_L - 2 * P.WALL
INNER_W = P.TRAY_W - 2 * P.WALL
BOARD_X0 = -INNER_L / 2 + 1.2                     # USB end of the board (left)
BOARD_X1 = BOARD_X0 + P.ESP_L                     # antenna end (right)
BOARD_YC = P.BOARD_Y
PINS_FROM_ANT = 18.5                              # centre of the used header pins, from the antenna end
WHEEL_X = BOARD_X1 - PINS_FROM_ANT                # the wheel stands over those pins

# wheel housing: tunnel, glass, PCB, then the bay for the Dupont connectors
Y_GLASS = P.WHEEL_TUBE
Y_PCB = Y_GLASS + P.LCD_GLASS_T
Y_BACK = Y_PCB + P.LCD_PCB_T                      # back face of the display PCB
WHEEL_DEPTH = Y_BACK + P.LCD_REAR_SPACE           # ring and foot depth
H_CENTER = P.FOOT_H + P.WHEEL_D / 2               # ring axis height above the foot base
WHEEL_H = P.FOOT_H + P.WHEEL_D
POCKET_D = 1.2                                    # depth of the foot seat in the lid
WHEEL_Z = TRAY_H - POCKET_D                       # assembly Z of the foot base
BAY_TOP = H_CENTER - P.LCD_PCB_D / 2 + P.LCD_PIN_Z + 4.0   # height of the bay in the foot
COVER_Y0 = WHEEL_DEPTH + P.CAP_T
COVER_Y1 = Y_BACK + max(P.BAY_L, P.LCD_CONN_LEN + 8.0)
COVER_HW = P.BAY_W / 2 + P.COVER_WALL             # half width of the cover (outside)
WHEEL_Y = BOARD_YC - Y_BACK - P.BAY_L / 2         # the lid slot is centred on the board

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

    # ESP32 upside down: four small posts under its corners carry it (the module, USB-C
    # and buttons hang below, in the free space between them), four snap hooks clamp it
    yc = BOARD_YC
    hw = P.ESP_W / 2
    fz = P.FLOOR - 0.1
    for xa in (BOARD_X0, BOARD_X1 - 3.0):
        for ya in (yc - hw, yc + hw - 3.0):
            t += box(xa, xa + 3.0, ya, ya + 3.0, fz, BOARD_BOT)
    za = BOARD_TOP + 0.2                       # underside of the hook lips
    for xa in (BOARD_X0 + 0.2, BOARD_X1 - 3.2):
        for s in (-1, 1):
            y_in = yc + s * (hw + 0.3)
            y_out = y_in + s * 1.2
            beam = box(xa, xa + 3.0, min(y_in, y_out), max(y_in, y_out), fz, za + 1.4)
            if vol(beam - cavity) > 0.5:
                raise ValueError("an ESP32 hook falls outside the tray cavity: "
                                 "increase TRAY_W or lower BOARD_Y")
            tip = y_in - s * 1.0               # the lip reaches 1 mm over the PCB, ramp on top
            pl = Plane.YZ.offset(xa + 1.5)
            lip = extrude(pl * Polygon((y_in + s * 0.2, za), (tip, za), (tip, za + 0.4),
                                       (y_in + s * 0.2, za + 1.4), align=None), amount=1.5, both=True)
            t += beam + lip
    t += box(BOARD_X1 + 0.3, BOARD_X1 + 1.5, yc - 8, yc + 8, fz, BOARD_TOP + 0.8)   # end stop

    # USB-C opening in the left wall: the port is under the PCB, centred on the board
    zc = BOARD_BOT - P.USB_AXIS_BELOW_PCB
    t -= box(-P.TRAY_L / 2 - 1, -INNER_L / 2 + 1, yc - P.USB_HOLE_W / 2, yc + P.USB_HOLE_W / 2,
             P.FLOOR, zc + P.USB_HOLE_H / 2)
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
    # big slot: the Dupont connectors of the ESP32 poke up through it
    lid_ -= box(WHEEL_X - P.BAY_W / 2, WHEEL_X + P.BAY_W / 2, WHEEL_Y + Y_BACK,
                WHEEL_Y + Y_BACK + P.BAY_L, SEAT_Z - 1, TRAY_H + 1)
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
    # the connectors go through here: a U shaped notch open at the bottom of the cap
    zb = H_CENTER - P.LCD_PCB_D / 2
    c -= box(-P.BAY_W / 2 + 4, P.BAY_W / 2 - 4, Y_BACK - 1, WHEEL_DEPTH + P.CAP_T + 1,
             -1, zb + P.LCD_PIN_Z + 7.0)
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
    yc = BOARD_YC
    hw = P.ESP_W / 2
    b = box(BOARD_X0, BOARD_X1, yc - hw, yc + hw, BOARD_BOT, BOARD_TOP)
    # underside: module at the antenna end, USB-C at the left end
    b += box(BOARD_X1 - 25.5, BOARD_X1, yc - 9, yc + 9, BOARD_BOT - 3.3, BOARD_BOT)
    b += box(BOARD_X0 - 1.0, BOARD_X0 + 5, yc - 4.5, yc + 4.5, BOARD_BOT - 3.3, BOARD_BOT)
    # pin headers, then the Dupont connectors on the pins in use (positions 2 to 12 of one
    # row, and position 1 of the other row, counted from the antenna end)
    for s in (-1, 1):
        y = yc + s * 11.43
        b += box(BOARD_X0 + 3.3, BOARD_X1 - 3.3, y - 1.27, y + 1.27, BOARD_TOP, BOARD_TOP + P.ESP_HDR_H)
    xk = lambda k: BOARD_X1 - 4.6 - (k - 1) * 2.54
    top = BOARD_TOP + P.DUPONT_H
    b += box(xk(12) - 1.27, xk(2) + 1.27, yc + 11.43 - 1.27, yc + 11.43 + 1.27, BOARD_TOP, top)
    b += box(xk(1) - 1.27, xk(1) + 1.27, yc - 11.43 - 1.27, yc - 11.43 + 1.27, BOARD_TOP, top)
    return b


def lcd_ghost():
    """Dummy GC9A01 module with its 7 Dupont connectors, in wheel coordinates."""
    zc = H_CENTER
    pcb = cyl_y(P.LCD_PCB_D, Y_PCB, Y_BACK, z=zc)
    glass = cyl_y(P.LCD_GLASS_D, Y_GLASS, Y_PCB, z=zc)
    zp = zc - P.LCD_PCB_D / 2 + P.LCD_PIN_Z
    conn = box(-8.9, 8.9, Y_BACK, Y_BACK + P.LCD_CONN_LEN, zp - 1.27, zp + 1.27)
    return pcb + glass + conn

