# Imports
try:
    from pynq.overlays.base import BaseOverlay
    from pynq.lib.arduino import Arduino_IO
    from pynq.lib import PynqMicroblaze
    from time import sleep
    print("Excellent. Successfully imported all dependencies.")
except ImportError as identifier:
    print("TracSat stopped. Failed to import a required dependency. See the error below: ")
    print(identifier)
    exit(1)

base = BaseOverlay("base.bit")
# Set up solenoids
sol1 = Arduino_IO(base.iop_arduino.mb_info, 0, 'out')
sol2 = Arduino_IO(base.iop_arduino.mb_info, 1, 'out')

print("Testing")

while True:
    print()
    print("Turning on solenoids")

    sol1.write(0x01)
    sol2.write(0x01)

    sleep(1.0)
    print("Turning off solenoids")

    sol1.write(0x00)
    sol2.write(0x00)

    sleep(5)