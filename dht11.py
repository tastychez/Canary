import adafruit_dht
import board

from config import dht11_pin, dht11_temp_threshold, dht11_humidity_threshold

# --- DHT11 Temperature & Humidity Sensor ---
# Single-wire digital sensor providing temperature (°C) and humidity (% RH).
# DATA pin is connected to the GPIO specified in config.json.
dht = adafruit_dht.DHT11(getattr(board, dht11_pin))


def read():
    """
    Return (temperature_c, humidity_pct) from the DHT11.

    The DHT11 is a slow sensor (~1 read/sec) and occasionally fails with a
    RuntimeError.  On failure this returns (None, None) so the caller can
    decide how to handle a missing reading.
    """
    try:
        return dht.temperature, dht.humidity
    except RuntimeError:
        return None, None


def is_alert():
    """
    Return True when temperature or humidity exceeds the configured
    safety thresholds.

    A failed sensor read is treated as *not* an alert to avoid
    false positives from transient communication errors.
    """
    temp, hum = read()
    if temp is None or hum is None:
        return False
    return temp >= dht11_temp_threshold or hum >= dht11_humidity_threshold
