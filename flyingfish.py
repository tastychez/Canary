import board
import digitalio
import time

flyingfish = digitalio.DigitalInOut(board.D2)  # Connect sensor D0 here
flyingfish.direction = digitalio.Direction.INPUT

