import time
import board
import digitalio

# Configure Digital Input
fc22 = digitalio.DigitalInOut(board.D2)
fc22.direction = digitalio.Direction.INPUT
