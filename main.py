import time

import led_matrix
from dht11 import is_alert as dht11_alert
from fc22sbx import fc22
from flyingfish import flyingfish

# ── Sensor helpers ─────────────────────────────────────────────────────────────


def any_sensor_triggered():
    """
    Return True if at least one sensor reports a detection event.

    Sensor polarity
    ---------------
    FC-22 (smoke / gas)    – active LOW: DO pulls LOW when gas detected
    Flying Fish (moisture) – active LOW: DO pulls LOW when water detected
    DHT11 (temp/humidity)  – alert when readings exceed configured thresholds
    """
    fc22_alert = not fc22.value  # LOW → smoke / gas present
    fish_alert = not flyingfish.value  # LOW → moisture present
    heat_or_humid = dht11_alert()  # True → temp or humidity too high
    return fc22_alert or fish_alert or heat_or_humid


# ── Output helpers ─────────────────────────────────────────────────────────────


def show_alert():
    """
    All LEDs ON = danger  (red equivalent on the monochrome matrix).
    A fully-lit 8×8 matrix is the brightest, most eye-catching state.
    """
    led_matrix.fill_all()


def show_safe():
    """
    All LEDs OFF = all clear  (green equivalent on the monochrome matrix).
    A blank display means no sensor has fired.
    """
    led_matrix.clear()


# ── Startup ────────────────────────────────────────────────────────────────────
show_safe()

# ── Main loop ─────────────────────────────────────────────────────────────────
# _last_triggered tracks the previous sensor state so we only push a new frame
# to the matrix when the state actually changes, avoiding unnecessary SPI writes
# and visible flicker.
_last_triggered = None

while True:
    triggered = any_sensor_triggered()

    if triggered != _last_triggered:
        if triggered:
            show_alert()
        else:
            show_safe()
        _last_triggered = triggered

    time.sleep(0.1)  # poll every 100 ms
