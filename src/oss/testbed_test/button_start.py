#from pynq.lib.button import read()
#from pynq.lib.button import wait_for_value(value)
#from pynq.lib.button import _impl

import video

from pynq.overlays.base import BaseOverlay
from pynq.lib import LED, Switch, Button


base = BaseOverlay("base.bit")

#define variables
#led0 = base.leds[0]
MAX_LEDS = 4
MAX_BUTTONS = 4
leds = [base.leds[index] for index in range(MAX_LEDS)]
buttons = [base.buttons[index] for index in range(MAX_BUTTONS)]


print("Waiting for button press")

leds[3].on()

while (base.buttons[0].read() == 0):
    continue

# Run Program Here
leds[0].on()
#subprocess.call("video.py", shell = True)
exec(open("video.py").read())

while (base.buttons[0].read() == 1):
    continue

#while (base.buttons[0].read() == 0):
#    continue

print("Program Success")

leds[3].off()
leds[0].off()

