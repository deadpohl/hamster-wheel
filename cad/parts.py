"""Parametric parts of the hamster wheel desk toy (build123d): tray, platform, wheel, cap.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Every builder returns a solid in ASSEMBLY coordinates unless noted:
  X = left/right, Y = front (negative, toward the viewer) to back, Z = up,
  origin = centre of the tray footprint, Z = 0 on the table.
build_all.py reorients each part for printing. The cage lives in cage.py.

How it is laid out (plain Dupont jumper wires, no soldering):
  * the tray is an open tub. Its top is the groove the cage plugs into;
  * the ESP32 lies upside down on the floor of the tray, pins up, resting on its module
    and USB-C socket, in a low pocket. Two dots of hot glue hold it;
  * a flat platform rests on a ledge above the ESP32 and its Dupont connectors, below the
    rim. The wheel stands on it, and a pinch of real wood shavings hides it;
  * the display connectors point straight back out of the wheel foot, under a small cover.
    The wires go down through a slot in the platform, open at its back edge: they slide in
    without unplugging anything.
"""
from math import atan, degrees, hypot

from build123d import Align, Box, Cone, Cylinder, Location, Plane, Polygon, Pos, Rot, extrude

import params as P

MIN = (Align.MIN, Align.MIN, Align.MIN)
CEN = (Align.CENTER, Align.CENTER, Align.MIN)
SQ = 2 - 2 ** 0.5   # change of a 45 degree chamfer per mm of outline offset

# ------------------------------------------------------------ derived values
BOARD_BOT = P.FLOOR + P.ESP_UNDER_H               # underside of the ESP32 PCB (it faces down)
BOARD_TOP = BOARD_BOT + P.ESP_PCB_T               # pin side of the PCB
PLATE_Z0 = BOARD_TOP + P.DUPONT_H + P.WIRE_BEND   # underside of the platform
PLATE_TOP = PLATE_Z0 + P.PLATE_T
INNER_W = P.TRAY_W - 2 * P.WALL
# The ESP32 mount and model are built in a BOARD frame: X along the PCB, from its USB end (0)
# to its antenna end (ESP_L), Y across from the centre line, Z as in the assembly. BOARD_LOC
# turns it so the USB end faces the back wall (the USB-C nose ends just inside the wall) and
# the pin row with the GPIOs faces +X, toward the wheel.
USB_MARGIN = max(1.4, P.USB_NOSE + 0.3)           # inner face of the wall to the USB end of the PCB
BOARD_LOC = Pos(P.BOARD_X, INNER_W / 2 - USB_MARGIN, 0) * Rot(Z=-90)
ROW_DY = 12.7                                     # pin rows, from the board centre line (25.4 apart)

# wheel housing: tunnel, glass, PCB, then room behind the PCB
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
POCKET_D = 1.2                                    # depth of the foot seat in the platform
WHEEL_Z = PLATE_TOP - POCKET_D                    # assembly Z of the foot base
BAY_TOP = PIN_Z + 1.27 + 3.0                      # height of the bay behind the display PCB
CAP_CUT = PIN_Z + 1.27 + 0.5                      # the cap is cut flat here, over the display connectors
HOLE_Y1 = Y_BACK + P.LCD_CONN_LEN + P.WIRE_BEND_LCD   # back end of the room for the wires (wheel frame)
WHEEL_X = P.WHEEL_X
WHEEL_Y = P.WHEEL_Y
# connector cover and wire slot (wheel frame): the cover walls stand on the platform beside
# the slot, a lip under each wall drops into the slot and holds the cover in place
CONN_HW = 7 * 2.54 / 2                            # half width of the 7 display connectors
COVER_IN = CONN_HW + 0.5                          # inner face of the cover walls
COVER_LIP = 1.2                                   # lip width
COVER_WALL = 2.4                                  # wall thickness (the inner half is the lip)
COVER_T = 1.6                                     # roof and back wall thickness
SLOT_HW = COVER_IN + COVER_LIP + P.COVER_FIT      # half width of the wire slot
SLOT_Y0 = Y_BACK + 0.5                            # front end of the slot, under the bay of the foot

# Rim: the tray wall is the outer side of the cage groove, a thin inner wall the other side.
# Under the groove a solid band holds that inner wall; under the band a ledge carries the
# platform. The walls lean out by FLARE, so the top outline is outline(FLARE). Offsets are
# distances inward from the tray outline at the BOTTOM (they include the flare).
GROOVE_Z = WHEEL_Z + P.FOOT_H - P.RING_OVER_GROOVE   # floor of the cage groove
RIM_Z = GROOVE_Z + P.GROOVE_WALL_H                   # top of the inner wall
TRAY_H = RIM_Z - 2.0                                 # top of the tray wall: lower, it guides the cage in
FLARE_DEG = degrees(atan(P.FLARE / TRAY_H))          # lean of the walls
GROOVE_W = P.CAGE_T + 2 * P.CAGE_FIT
TOP_WALL_OFF = P.WALL - P.FLARE                      # inner face of the wall at the top (outer side of the groove)
CAGE_OFF = TOP_WALL_OFF + P.CAGE_FIT                 # outer face of the cage walls
GROOVE_IN_OFF = TOP_WALL_OFF + GROOVE_W              # inner face of the groove
RIM_IN_OFF = GROOVE_IN_OFF + P.GROOVE_WALL_W         # inner face of the inner wall and of the band
PLATE_OFF = RIM_IN_OFF + P.PLATE_FIT                 # edge of the platform
LEDGE_OFF = PLATE_OFF + P.LEDGE_W                    # inner edge of the ledge
if GROOVE_Z < PLATE_TOP + 0.5:
    raise ValueError("the cage groove would be below the platform: increase FOOT_H")


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


def tapered(pts, z0, h, taper):
    """Extrusion of an outline from z0 up by h, its sides at `taper` degrees (positive = shrinks)."""
    return Pos(0, 0, z0) * extrude(Polygon(*pts[::-1], align=None), amount=h, taper=taper)


def edges(pts):
    """Yield (midpoint, unit tangent, outward normal, length) of each edge of a clockwise polygon."""
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        ln = hypot(q[0] - p[0], q[1] - p[1])
        tx, ty = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
        yield ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), (tx, ty), (-ty, tx), ln


# --------------------------------------------------------------------- tray
def tray():
    c = P.LEAD_IN
    # the walls lean out, the floor keeps the bottom outline. Above the groove floor the inner
    # face is vertical: that is the outer side of the groove
    t = tapered(outline(0), 0, TRAY_H, -FLARE_DEG)
    cavity = tapered(outline(-P.WALL), 0, GROOVE_Z + 0.01, -FLARE_DEG) - prism(outline(20), -1, P.FLOOR)
    t -= cavity + prism(outline(-TOP_WALL_OFF), GROOVE_Z, TRAY_H + 1)
    # lead-in: the groove side of the wall is chamfered at the top
    t -= tapered(outline(-TOP_WALL_OFF), TRAY_H - c, c + 0.01, -45)

    # band under the groove: its inner face surrounds the platform, its bottom is the ledge
    # the platform rests on, with a 45 degree chamfer under it down to the wall (no support)
    h = 14.0
    band = cavity & prism(outline(20), PLATE_Z0 - h, GROOVE_Z)
    band -= prism(outline(-RIM_IN_OFF), PLATE_Z0, GROOVE_Z + 1)
    band -= tapered(outline(-LEDGE_OFF + h), PLATE_Z0 - h - 0.01, h + 0.02, 45)
    # inner wall of the groove, chamfered at the top on the groove side
    inner = prism(outline(-GROOVE_IN_OFF), GROOVE_Z - 0.1, RIM_Z - c) \
        + tapered(outline(-GROOVE_IN_OFF), RIM_Z - c, c, 45)
    inner -= prism(outline(-RIM_IN_OFF), GROOVE_Z - 1, RIM_Z + 1)
    t += band + inner

    # one dimple per long wall (not the corner chamfers), where the snap bump of the cage clicks in
    for (mx, my), (tx, ty), (nx, ny), ln in edges(outline(-GROOVE_IN_OFF)):
        if ln > 20:
            pl = Plane(origin=(mx, my, GROOVE_Z + 2.5), x_dir=(tx, ty, 0), z_dir=(-nx, -ny, 0))
            t -= Location(pl) * (Pos(0, 0, -0.1) * Cone(
                P.BUMP_R + 0.6, P.BUMP_R + 0.1, P.DIMPLE_D + 0.2, align=CEN))

    keep = prism(outline(-P.WALL + 0.5), 0, TRAY_H)   # features may merge into the walls, never stick out
    feats, cuts = _esp_mount()
    t += (BOARD_LOC * feats) & keep
    # USB-C opening in the back wall, open at the bottom: the plug body is taller than the
    # socket and reaches below the floor level
    cuts += box(-USB_MARGIN - P.WALL - P.FLARE - 2, -USB_MARGIN + 0.5,
                -P.USB_HOLE_W / 2, P.USB_HOLE_W / 2, -1, BOARD_TOP + 2.5)
    return t - BOARD_LOC * cuts


def _esp_mount():
    """ESP32 pocket in the BOARD frame: (features to add, cuts)."""
    # ESP32 upside down, resting on its module and USB-C socket, in a snug pocket: the posts
    # at the USB end and the stops at the antenna end hold it by friction, the long walls
    # keep it straight. Nothing clips (the header plastic covers the long edges).
    yc, x0, x1 = 0.0, 0.0, P.ESP_L
    hw = P.ESP_W / 2
    zt = BOARD_TOP
    fz = P.FLOOR - 0.1
    g = P.ESP_GAP
    t = P.ESP_WALL_T
    feats = []
    # long walls beside the PCB and the header plastic, with a lead-in chamfer at the top
    wz1 = zt + P.ESP_WALL_H
    for s in (-1, 1):
        yi = yc + s * (hw + g)
        prof = [(yi, fz), (yi + s * t, fz), (yi + s * t, wz1), (yi + s * 0.9, wz1), (yi, wz1 - 0.9)]
        feats.append(Pos((x0 + x1) / 2, 0, 0) * extrude(
            Plane.YZ * Polygon(*prof, align=None), amount=(x1 - x0 - 8) / 2, both=True))
    # USB end: two posts against the PCB end, on both sides of the USB-C socket
    for s in (-1, 1):
        a, b = yc + s * 6.6, yc + s * 10.8
        feats.append(box(-USB_MARGIN - 0.5, x0 - g, min(a, b), max(a, b), fz, wz1))
    # antenna end: two thick stops beside the antenna, snug against the PCB end, a little
    # higher than the PCB with a lead-in chamfer
    xs = x1 + P.ESP_STOP_GAP
    st = t + 1.0
    sz = zt + 1.5
    prof = [(xs, fz), (xs + st, fz), (xs + st, sz), (xs + 0.6, sz), (xs, sz - 0.6)]
    ah = P.ESP_ANT_W / 2 + 0.6
    for s in (-1, 1):
        a, b = yc + s * ah, yc + s * (hw + g + t)
        feats.append(Pos(0, (a + b) / 2, 0) * extrude(
            Plane.XZ * Polygon(*prof, align=None), amount=abs(b - a) / 2, both=True))

    cuts = []
    # pockets under the EN and BOOT buttons, so they can never be pressed by the floor
    for s in (-1, 1):
        a, b = yc + s * 5.0, yc + s * 11.5
        cuts.append(box(x0 - 0.2, x0 + 7.5, min(a, b), max(a, b), P.FLOOR - 1.2, P.FLOOR + 0.1))
    # the pin headers stick out a little past the PCB end: a relief in the stops, above the PCB
    for s in (-1, 1):
        y = yc + s * ROW_DY
        cuts.append(box(xs - 0.1, x1 + 1.0, y - 1.6, y + 1.6, zt, sz + 1))
    return fuse_all(feats), fuse_all(cuts)


def esp_fit_test():
    """The ESP32 pocket alone on a piece of floor, in the BOARD frame: a quick print to check
    the friction fit before printing the whole tray."""
    feats, cuts = _esp_mount()
    m = 1.5
    hw = P.ESP_W / 2 + P.ESP_GAP + P.ESP_WALL_T + m
    plate = box(-USB_MARGIN - 0.5 - m, P.ESP_L + P.ESP_STOP_GAP + P.ESP_WALL_T + 1.0 + m, -hw, hw, 0, P.FLOOR)
    return plate + feats - cuts


# ----------------------------------------------------------------- platform
def platform(grip=True):
    """grip=False leaves out the friction ribs (they overlap the tray on purpose)."""
    p = prism(outline(-PLATE_OFF), PLATE_Z0, PLATE_TOP)
    # friction fit: small conical ribs on the edge, two on each long side, one on each short
    # side. Narrow at the bottom, so they guide the platform in, then press into the wall
    if grip and P.PLATE_GRIP > 0:
        r = 1.5
        a = P.TRAY_L / 2 - PLATE_OFF + P.PLATE_FIT + P.PLATE_GRIP - r
        b = P.TRAY_W / 2 - PLATE_OFF + P.PLATE_FIT + P.PLATE_GRIP - r
        # (the ribs on the long sides stay clear of the wire slot)
        spots = [(x, s * b) for x in (-P.TRAY_L / 3, P.TRAY_L / 3) for s in (-1, 1)] + [(s * a, 0) for s in (-1, 1)]
        for x, y in spots:
            p += Pos(x, y, PLATE_Z0) * Cone(r - 0.4, r, P.PLATE_T, align=CEN)
    seat = box(WHEEL_X - P.FOOT_W / 2 - 0.25, WHEEL_X + P.FOOT_W / 2 + 0.25,
               WHEEL_Y - 0.25, WHEEL_Y + WHEEL_DEPTH + 0.25, WHEEL_Z, PLATE_TOP + 1)
    # wire slot from under the bay of the foot to the back edge: the wires slide in, nothing
    # to unplug. The lips of the connector cover drop into it
    slot = box(WHEEL_X - SLOT_HW, WHEEL_X + SLOT_HW, WHEEL_Y + SLOT_Y0, P.TRAY_W,
               PLATE_Z0 - 1, PLATE_TOP + 1)
    inside = prism(outline(-PLATE_OFF - 2.0), PLATE_Z0 - 2, PLATE_TOP + 2)
    cover_back = box(WHEEL_X - 1, WHEEL_X + 1, WHEEL_Y + HOLE_Y1, WHEEL_Y + HOLE_Y1 + COVER_T, PLATE_Z0, PLATE_TOP)
    if vol(seat + cover_back - inside) > 0.1:
        raise ValueError("the wheel and its connector cover do not fit on the platform: "
                         "check WHEEL_X / WHEEL_Y, or increase TRAY_L / TRAY_W")
    return p - seat - slot


# -------------------------------------------------------------------- wheel
def _screw_r():
    return (P.WHEEL_D / 2 + (P.LCD_PCB_D / 2 + P.FIT)) / 2


def wheel():
    """Ring housing and straight foot, in WHEEL coordinates (X centred, Y front=0, Z base=0)."""
    fw = P.FOOT_W / 2
    body = cyl_y(P.WHEEL_D, 0, WHEEL_DEPTH, z=H_CENTER) + box(-fw, fw, 0, WHEEL_DEPTH, 0, H_CENTER)
    # window, glass seat, PCB seat
    body -= cyl_y(P.WHEEL_WINDOW_D, -1, Y_GLASS + 1, z=H_CENTER)
    body -= Pos(0, 0, H_CENTER) * (Rot(X=-90) * Cone(
        P.WHEEL_WINDOW_D / 2 + P.WHEEL_FLARE, P.WHEEL_WINDOW_D / 2, P.WHEEL_FLARE, align=CEN))
    body -= cyl_y(P.LCD_GLASS_D + 2 * P.FIT, Y_GLASS, Y_PCB + 0.01, z=H_CENTER)
    body -= cyl_y(P.LCD_PCB_D + 2 * P.FIT, Y_PCB, WHEEL_DEPTH + 1, z=H_CENTER)
    # the tab at the bottom of the display PCB: its slot starts at the same depth as the glass
    # seat (no step to catch the bottom of the glass or its ribbon). Under it the foot is
    # solid, 1 mm below the tab: a full flat bottom to glue the wheel on the platform
    tw = P.LCD_TAB_W / 2 + P.FIT
    body -= box(-tw, tw, Y_GLASS, WHEEL_DEPTH + 1, TAB_BOT - 1.0, H_CENTER)
    # bay behind the PCB: the Dupont connectors point straight back, out of the foot. It is
    # open at the bottom, over the wire slot of the platform
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
    # cut flat just above the display connectors, which leave under it. The boss is cut away
    # in front of the tab up to the centre, the same slot as in the wheel: it only presses on
    # the round part of the PCB, beside and above the tab
    c -= box(-P.WHEEL_D, P.WHEEL_D, Y_BACK - 1, WHEEL_DEPTH + P.CAP_T + 1, -1, CAP_CUT)
    tw = P.LCD_TAB_W / 2 + P.FIT
    c -= box(-tw, tw, Y_BACK - 1, WHEEL_DEPTH, -1, H_CENTER)
    if P.CAP_SCREWS:
        for s in (-1, 1):
            c -= cyl_y(2.4, WHEEL_DEPTH - 1, WHEEL_DEPTH + P.CAP_T + 1, x=s * _screw_r(), z=zc)
    return c


def cover():
    """Cover over the display connectors, behind the wheel cap, in WHEEL coordinates. Open at
    the front (the connectors come in) and at the bottom (the wires go down the slot). A lip
    under each wall drops into the slot of the platform and holds it."""
    zb = POCKET_D                           # top of the platform
    zr = PIN_Z + 1.27 + 0.6                 # underside of the roof, over the connectors
    zt = zr + COVER_T
    yf = WHEEL_DEPTH + P.CAP_T + 0.3        # just behind the cap flange
    yb = HOLE_Y1 + COVER_T
    wo = COVER_IN + COVER_WALL
    c = box(-wo, wo, yf, yb, zb, zt) - box(-COVER_IN, COVER_IN, yf - 1, HOLE_Y1, zb - 1, zr)
    # soft top edges (sides and back): it looks less like a box in the shavings
    for s in (-1, 1):
        c -= Pos(s * wo, (yf + yb) / 2, zt) * (Rot(Y=45) * Box(2.83, yb - yf + 2, 2.83))
    c -= Pos(0, yb, zt) * (Rot(X=45) * Box(2 * wo + 2, 2.83, 2.83))
    for s in (-1, 1):
        a, b = s * COVER_IN, s * (COVER_IN + COVER_LIP)
        c += box(min(a, b), max(a, b), yf, yb, zb - P.PLATE_T + 0.6, zb + 0.01)
    return c


def place_wheel(shape):
    """Move a wheel-frame part to its assembly position."""
    return Pos(WHEEL_X, WHEEL_Y, WHEEL_Z) * shape


# ---------------------------------------------------------- reference models
def esp32_ghost():
    """Dummy ESP32 board (upside down) with its Dupont connectors, for fit checks and previews."""
    yc, x0, x1 = 0.0, 0.0, P.ESP_L
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
    return BOARD_LOC * b


def lcd_ghost():
    """Dummy GC9A01 module with its 7 Dupont connectors, in wheel coordinates."""
    zc = H_CENTER
    pcb = cyl_y(P.LCD_PCB_D, Y_PCB, Y_BACK, z=zc)
    pcb += box(-P.LCD_TAB_W / 2, P.LCD_TAB_W / 2, Y_PCB, Y_BACK, TAB_BOT, zc)
    glass = cyl_y(P.LCD_GLASS_D, Y_GLASS, Y_PCB, z=zc)
    conn = box(-CONN_HW, CONN_HW, Y_BACK, Y_BACK + P.LCD_CONN_LEN, PIN_Z - 1.27, PIN_Z + 1.27)
    return pcb + glass + conn
