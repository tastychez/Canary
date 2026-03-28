import board
import digitalio
import time

sensor = digitalio.DigitalInOut(board.D2)  # Connect sensor D0 here
sensor.direction = digitalio.Direction.INPUT

while True:
    detected = not sensor.value  # Active LOW — invert for intuitive True/False
    print("Detected!" if detected else "Nothing detected")
    time.sleep(0.2)