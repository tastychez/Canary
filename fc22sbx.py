import board
import digitalio

from config import fc22_pin, fc22_2_pin

fc22 = digitalio.DigitalInOut(getattr(board, fc22_pin))
fc22.direction = digitalio.Direction.INPUT
fc22.pull = digitalio.Pull.UP

fc22_2 = digitalio.DigitalInOut(getattr(board, fc22_2_pin))
fc22_2.direction = digitalio.Direction.INPUT
fc22_2.pull = digitalio.Pull.UP
