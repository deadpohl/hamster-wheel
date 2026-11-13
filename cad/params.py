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
# Its header pins stick out of the BACK of the PCB, so the Dupont connectors point
# straight backwards: the wheel has a bay behind the PCB for them.
LCD_PCB_D = 38.0        # measure me: outer diameter of the round PCB
LCD_GLASS_D = 35.6      # measure me: diameter of the glass on top of the PCB
LCD_ACTIVE_D = 32.4     # visible picture diameter (datasheet value)
LCD_PCB_T = 1.6         # measure me: PCB thickness
LCD_GLASS_T = 1.8       # measure me: glass height above the PCB
LCD_REAR_SPACE = 6.0    # room behind the PCB inside the ring
LCD_CONN_LEN = 16.5     # measure me: Dupont housing + header plastic, behind the PCB
LCD_PIN_Z = 2.7         # measure me: height of the pin row above the bottom edge of the PCB
BAY_W = 36.0            # width of the wire bay behind the display (and of the slot in the lid)
BAY_L = 26.0            # length of that bay, from the back of the PCB

# ------------------------------------------------------------------ ESP32
# 38 pin DevKit style board. It lies UPSIDE DOWN on the floor of the tray: pins up,
# so the Dupont connectors plug in from above and go straight up through the lid.
ESP_L = 55.0            # measure me: board length (48 to 55 depending on the clone)
ESP_W = 28.5            # measure me: board width (25 to 29 depending on the clone)
ESP_PCB_T = 1.6
ESP_UNDER_H = 4.5       # measure me: tallest part under the board (module, USB-C, buttons)
ESP_HDR_H = 2.5         # height of the black plastic of the pin headers
DUPONT_H = 17.0         # measure me: Dupont connector height above the PCB (header + housing)
USB_HOLE_W = 11.5       # opening for the USB-C plug body (plug is about 10.5 wide)
USB_HOLE_H = 7.0        # opening height (plug is about 6.5 high)
USB_AXIS_BELOW_PCB = 1.7  # the USB-C port is under the PCB, its axis this far below it
CLEAR_ABOVE = 1.5       # free height between the header plastic and the lid

# ------------------------------------------------------------------- tray
TRAY_L = 90.0           # outer size along X
TRAY_W = 68.0           # outer size along Y, front to back (room for the wheel bay and shavings)
CORNER_CUT = 8.0        # 45 degree chamfer on the four vertical corners (0 = square corners)
WALL = 2.8              # wall thickness
FLOOR = 2.0
BOARD_Y = 7.0           # ESP32 position along Y (positive = toward the back)

# -------------------------------------------------------------------- lid
LID_T = 3.0             # lid plate thickness (also the depth of the seat in the tray)
LID_FIT = 0.2           # clearance between lid and tray seat, per side
LID_BORDER_H = 7.0      # height of the raised rim of the lid (the cage plugs into a groove in it)
LID_RIM_W = 1.2         # thickness of the two thin walls of the rim, the cage goes between them
SEAT_W = 1.4            # how far the seat steps in from the inner wall face

# ------------------------------------------------------------------ wheel
WHEEL_D = 48.0          # outer diameter of the wheel housing
WHEEL_TUBE = 6.0        # depth of the "tunnel" in front of the screen
WHEEL_WINDOW_D = LCD_ACTIVE_D + 1.0
WHEEL_FLARE = 1.5       # chamfer on the window so the tunnel does not clip the picture
FOOT_H = 5.0            # height of the foot below the ring
FOOT_W = 50.0
FIT = 0.25              # general radial clearance for pockets
CAP_T = 1.5             # rear cap flange thickness
CAP_SCREWS = True       # two M2 self tapping screws (optional, glue also works)
CAP_PRESS = 0.15        # radial clearance of the cap plug in the PCB pocket
COVER_H = 22.0          # inner height of the cover over the Dupont connectors
COVER_WALL = 2.0

# ------------------------------------------------------------------- cage
# Printed flat as one "net": the roof in the middle and one wall around each of
# its edges, joined by thin living hinges. Fold the walls up and plug them into the groove of the lid.
CAGE_T = 2.0            # thickness of every cage panel
BAR_W = 1.6             # bar width
WALL_PITCH = 11.0       # vertical bar spacing on the walls (large: you must see the wheel)
BELT_POS = 0.5           # height of the horizontal bar, all around: 0 = right under the top rail, 1 = just above the skirt
ROOF_PITCH = 14.0       # bar spacing on the roof
POST_W = 4.0            # solid post at each vertical edge of a wall
RAIL_W = 3.5            # solid top rail of the walls and border of the roof
RIM_H = 8.0             # solid skirt at the bottom of the walls, plugs into the groove of the lid
CAGE_FIT = 0.5          # clearance on each side of the skirt in the groove (the folded cage is floppy)
LEAD_IN = 0.6           # chamfer that guides the walls into the groove (mouth of the groove, skirt edge)
ROOF_GAP = 3.0          # free space between the wheel top and the cage roof
HINGES = True           # False: no hinge film, the panels print separately and you glue them
HINGE_FILM = 0.4        # thickness of the living hinge (2 layers at 0.2 mm). PETG recommended
HINGE_W = 1.6           # width of the hinge film (longer and thinner = less stress when folding)
FOLD_OFFSET = None       # how far a folded wall stands outside the edge of the roof (the bend of the hinge).
                        # None = computed from the hinge. If your folded cage does not drop into the groove,
                        # measure the real offset and set it here: the roof is sized from it
BUMP_R = 0.6            # snap bump on each wall (clicks into a dimple in the lid rim)
DIMPLE_D = 0.6          # depth of that dimple

