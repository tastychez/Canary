import time
import board
import digitalio

# Configure Digital Input
digital_pin = digitalio.DigitalInOut(board.D2)
digital_pin.direction = digitalio.Direction.INPUT

while True:
    # Read High/Low
    print(f"Digital Value: {digital_pin.value}")
    time.sleep(0.5)
