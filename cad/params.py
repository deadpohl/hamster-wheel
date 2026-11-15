# Hamster wheel desk toy: all printable dimensions, in millimetres.
# Author: DeadPohl  https://www.instagram.com/_deadpohl_
#
# Edit the values below, then run `python build_all.py` to regenerate ../stl.
# The defaults are best guesses from datasheets. Measure YOUR display and YOUR
# ESP32 board with calipers and adjust the "measure me" values first.
#
# Wiring uses ordinary female-female Dupont jumper wires on both ends, no soldering.

# ---------------------------------------------------------------- display
# GC9A01 1.28" round module, 7 pin version (VCC GND SCL SDA DC CS RST).
# The PCB is a disc with a tab at the bottom that carries the pins. The pins stick out
# of the BACK of the tab, so the Dupont connectors point straight backwards, out of the
# back of the wheel foot. The wires go down through a slot in the platform that is open at
# its back edge: they slide in without unplugging anything. A small cover hides the connectors.
LCD_PCB_D = 38.0        # measure me: diameter of the round part of the PCB
LCD_H_TOTAL = 45.0      # measure me: from the top of the disc to the bottom edge of the tab
LCD_TAB_W = 24.0        # measure me: width of the tab (the pocket is cut this wide, a bit more is fine)
LCD_GLASS_D = 35.6      # measure me: diameter of the glass on top of the PCB
LCD_ACTIVE_D = 32.4     # visible picture diameter (datasheet value)
LCD_PCB_T = 1.6         # measure me: PCB thickness
LCD_GLASS_T = 1.8       # measure me: glass height above the PCB
LCD_REAR_SPACE = 6.0    # room behind the PCB inside the ring
LCD_CONN_LEN = 16.5     # measure me: Dupont housing + header plastic, behind the PCB
LCD_PIN_Z = 1.5         # measure me: height of the pin row above the bottom edge of the tab
BAY_W = 25.0            # width of the bay behind the display, where the connectors leave the wheel
WIRE_BEND_LCD = 6.0     # room behind the display connectors for the wires to bend down

# ------------------------------------------------------------------ ESP32
# 38 pin DevKit style board. It lies UPSIDE DOWN on the floor of the tray: pins up, resting
# on its module and USB-C socket, in a snug pocket: a friction fit. Print esp_fit_test.stl
# first to check it (two dots of hot glue if it is loose). The Dupont connectors and the
# wires stay under the platform.
ESP_L = 48.0            # measure me: PCB length, WITHOUT the antenna
ESP_W = 28.0            # measure me: PCB width
ESP_ANT_L = 6.0         # measure me: how far the antenna sticks out past the end of the PCB
ESP_ANT_W = 18.0        # measure me: width of that antenna
ESP_PCB_T = 1.6
ESP_UNDER_H = 3.5       # measure me: board pins up on the table, height from the table to the UNDERSIDE of the PCB
ESP_HDR_H = 3.0         # height of the black plastic of the pin headers
DUPONT_H = 15.0         # measure me: top of a plugged Dupont connector above the PCB
WIRE_BEND = 8.0         # room above the Dupont connectors for the wires to bend
USB_NOSE = 1.5          # measure me: how far the USB-C socket sticks out past the end of the PCB
USB_HOLE_W = 12.5       # opening for the USB-C plug body (some cables have a big moulded end)
ESP_GAP = 0.3           # clearance around the PCB in its pocket
ESP_STOP_GAP = 0.0      # clearance between the antenna end of the PCB and its two stops (the friction fit)
ESP_WALL_T = 2.0        # thickness of the pocket walls and stops
ESP_WALL_H = 3.5        # height of the pocket walls above the PCB

# ------------------------------------------------------------------- tray
TRAY_L = 105.0          # outer size along X (longer than wide, like a real cage)
TRAY_W = 68.0           # outer size along Y, front to back
FLARE = 3.0             # the walls lean out: the top is this much wider than the bottom, per side (0 = straight)
CORNER_CUT = 0.0        # 45 degree chamfer on the four vertical corners (0 = square corners, like a real cage)
WALL = 2.8              # wall thickness
FLOOR = 2.0
BOARD_X = -22.0         # ESP32 position along X (its USB end faces the back wall, the cable leaves at the back)
WHEEL_X = 15.0          # wheel position along X (0 = centred). Off centre, to the right, away from
                        # the ESP32 connectors: the wires from the display have room to curl
WHEEL_Y = -8.0          # front face of the wheel along Y (0 = middle of the tray, negative = toward
                        # the front). Far enough back for the wire slot to reach the platform edge
# The top of the tray is the groove for the cage: the tray wall is its outer side, a thin
# inner wall is the other side.
GROOVE_WALL_H = 7.0     # height of the inner wall of the groove (the tray wall is 2 mm lower: it guides the cage in)
GROOVE_WALL_W = 1.2     # thickness of that inner wall

# --------------------------------------------------------------- platform
# A flat plate over the ESP32, below the rim of the tray. The wheel stands on it and a pinch
# of real wood shavings hides it. It rests on a ledge and lifts out with the wheel.
PLATE_T = 3.0           # platform thickness
PLATE_FIT = 0.2         # clearance around the platform, per side
PLATE_GRIP = 0.15       # six small ribs on the platform edge press this far into the wall: a friction fit
                        # (too tight: sand the ribs or lower it, too loose: raise it, 0 = no ribs)
LEDGE_W = 1.5           # how far the ledge under the platform reaches in
COVER_FIT = 0.05        # clearance of the lips of the connector cover in the platform slot, per side
RING_OVER_GROOVE = 3.8  # bottom of the wheel ring above the floor of the cage groove (3.8 keeps the
                        # cage height of the first version, an already printed cage still fits)

# ------------------------------------------------------------------ wheel
WHEEL_D = 48.0          # outer diameter of the wheel housing
WHEEL_TUBE = 6.0        # depth of the "tunnel" in front of the screen
WHEEL_WINDOW_D = LCD_ACTIVE_D + 1.0
WHEEL_FLARE = 1.5       # chamfer on the window so the tunnel does not clip the picture
FOOT_H = 7.0            # height of the straight foot below the ring (it stands in the shavings)
FOOT_W = 30.0           # foot width, a little more than the display tab
FIT = 0.25              # general radial clearance for pockets
CAP_T = 1.5             # rear cap flange thickness
CAP_SCREWS = True       # two M2 self tapping screws (optional, glue also works)
CAP_PRESS = 0.15        # radial clearance of the cap plug in the PCB pocket

# ------------------------------------------------------------------- cage
# Printed flat as one "net": the roof in the middle and one wall around each of
# its edges, joined by thin living hinges. Fold the walls up and plug them into the groove of the tray.
CAGE_T = 2.0            # thickness of every cage panel
BAR_W = 1.6             # bar width
WALL_PITCH = 11.0       # vertical bar spacing on the walls (large: you must see the wheel)
BELT_POS = 0.5           # height of the horizontal bar, all around: 0 = right under the top rail, 1 = just above the skirt
ROOF_PITCH = 14.0       # bar spacing on the roof
POST_W = 4.0            # solid post at each vertical edge of a wall
RAIL_W = 3.5            # solid top rail of the walls and border of the roof
RIM_H = 8.0             # solid skirt at the bottom of the walls, plugs into the groove of the tray
CAGE_FIT = 0.5          # clearance on each side of the skirt in the groove (the folded cage is floppy)
LEAD_IN = 0.6           # chamfer that guides the walls into the groove (mouth of the groove, skirt edge)
ROOF_GAP = 3.0          # free space between the wheel top and the cage roof
HINGES = True           # False: no hinge film, the panels print separately and you glue them
HINGE_FILM = 0.4        # thickness of the living hinge (2 layers at 0.2 mm). PETG is the safest, PLA held in a first test
HINGE_W = 1.6           # width of the hinge film (longer and thinner = less stress when folding)
FOLD_OFFSET = None       # how far a folded wall stands outside the edge of the roof (the bend of the hinge).
                        # None = computed from the hinge. If your folded cage does not drop into the groove,
                        # measure the real offset and set it here: the roof is sized from it
BUMP_R = 0.6            # snap bump on each wall (clicks into a dimple in the tray rim)
DIMPLE_D = 0.6          # depth of that dimple

