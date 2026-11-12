# Hamster wheel desk toy: all printable dimensions, in millimetres.
# Author: DeadPohl  https://www.instagram.com/_deadpohl_
#
# Edit the values below, then run `python build_all.py` to regenerate ../stl.
# The defaults are best guesses from datasheets. Measure YOUR display and YOUR
# ESP32 board with calipers and adjust the "measure me" values first.

# ---------------------------------------------------------------- display
# GC9A01 1.28" round module, 7 pin version (VCC GND SCL SDA DC CS RST)
LCD_PCB_D = 38.0        # measure me: outer diameter of the round PCB
LCD_GLASS_D = 35.6      # measure me: diameter of the glass on top of the PCB
LCD_ACTIVE_D = 32.4     # visible picture diameter (datasheet value)
LCD_PCB_T = 1.6         # measure me: PCB thickness
LCD_GLASS_T = 1.8       # measure me: glass height above the PCB
LCD_REAR_SPACE = 6.0    # room behind the PCB for header pins and soldered wires
LCD_PIN_SLOT_W = 20.0   # width of the notch for the 7 pin header (17.8 mm + margin)

# ------------------------------------------------------------------ ESP32
# 38 pin DevKit style board, USB-C at one short end
ESP_L = 55.0            # measure me: board length (48 to 55 depending on the clone)
ESP_W = 28.5            # measure me: board width (25 to 29 depending on the clone)
ESP_PCB_T = 1.6
ESP_PIN_LEN = 11.0      # measure me: how far the header pins stick out below the PCB
ESP_TOP_H = 4.0         # tallest part on top of the PCB (USB-C, buttons, module)
USB_HOLE_W = 11.5       # opening for the USB-C plug body (plug is about 10.5 wide)
USB_HOLE_H = 7.0        # opening height (plug is about 6.5 high)
USB_AXIS_ABOVE_PCB = 1.7  # height of the USB-C port axis above the PCB top

# ------------------------------------------------------------------- tray
TRAY_L = 94.0           # outer size along X (the wheel stands right above the ESP32)
TRAY_W = 60.0           # outer size along Y, front to back (room for the shavings)
CORNER_CUT = 10.0       # 45 degree chamfer on the four vertical corners (0 = square corners)
WALL = 2.8              # wall thickness
FLOOR = 2.0
WIRE_ROOM = 4.0         # free height between the ESP32 and the lid for wires
BOARD_Y = 4.0           # ESP32 position along Y (positive = toward the back, under the wire slot)

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
FOOT_H = 6.0            # height of the foot below the ring
FOOT_W = 50.0
WHEEL_X = 10.0          # wheel position on the lid (X)
WHEEL_Y = 4.0           # wheel front face position on the lid (Y, negative = toward viewer)
FIT = 0.25              # general radial clearance for pockets
CAP_T = 1.5             # rear cap flange thickness
CAP_SCREWS = True       # two M2 self tapping screws (optional, glue also works)
CAP_PRESS = 0.15        # radial clearance of the cap plug in the PCB pocket

# ------------------------------------------------------------------- cage
# Printed flat as one "net": the roof in the middle and one wall around each of
# its edges, joined by thin living hinges. Fold the walls up and plug them into the groove of the lid.
CAGE_T = 2.0            # thickness of every cage panel
BAR_W = 1.6             # bar width
WALL_PITCH = 11.0       # vertical bar spacing on the walls (large: you must see the wheel)
ROOF_PITCH = 14.0       # bar spacing on the roof
POST_W = 4.0            # solid post at each vertical edge of a wall
RAIL_W = 3.5            # solid top rail of the walls and border of the roof
RIM_H = 8.0             # solid skirt at the bottom of the walls, plugs into the groove of the lid
CAGE_FIT = 0.2          # clearance on each side of the skirt in the groove
ROOF_GAP = 3.0          # free space between the wheel top and the cage roof
HINGES = True           # False: no hinge film, the panels print separately and you glue them
HINGE_FILM = 0.6        # thickness of the living hinge (3 layers at 0.2 mm). PETG recommended
HINGE_W = 1.2           # width of the hinge film
BUMP_R = 0.6            # snap bump on each wall (clicks into a dimple in the lid rim)
DIMPLE_D = 0.5          # depth of that dimple

