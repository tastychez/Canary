"""
test_dht11.py
=============
Unit tests for dht11.py – DHT11 temperature & humidity sensor.

What is tested
--------------
* The correct board pin (from config.json) is passed to DHT11().
* read() returns (temperature, humidity) on success.
* read() returns (None, None) when the sensor raises RuntimeError.
* is_alert() fires when temperature or humidity exceeds the configured
  thresholds, and stays silent on normal readings or failed reads.
"""

import importlib
import sys
from unittest.mock import PropertyMock, patch

import pytest

# ── Hardware stubs (injected by tests/conftest.py) ────────────────────────────
mock_board = sys.modules["board"]
mock_adafruit_dht = sys.modules["adafruit_dht"]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def dht11_mod():
    """
    Import dht11.py exactly once per test-module session, with a clean mock.

    Evicting 'dht11' and 'config' from sys.modules before import guarantees
    module-level code re-executes against freshly-reset hardware stubs.
    """
    for name in ("dht11", "config"):
        sys.modules.pop(name, None)

    mock_adafruit_dht.reset_mock()

    mod = importlib.import_module("dht11")
    yield mod

    for name in ("dht11", "config"):
        sys.modules.pop(name, None)


# ── Initialisation ────────────────────────────────────────────────────────────


class TestDHT11Initialisation:
    def test_dht_object_exists(self, dht11_mod):
        """Module must expose a top-level `dht` sensor object."""
        assert hasattr(dht11_mod, "dht"), (
            "dht11.py should define a module-level variable named 'dht'"
        )

    def test_dht11_called_with_correct_pin(self, dht11_mod):
        """DHT11() must receive the pin matching 'dht11_pin' in config.json."""
        import config

        mock_adafruit_dht.DHT11.assert_called_once_with(
            getattr(mock_board, config.dht11_pin)
        )


# ── read() ────────────────────────────────────────────────────────────────────


class TestRead:
    def test_returns_temperature_and_humidity(self, dht11_mod):
        mock_dht = dht11_mod.dht
        type(mock_dht).temperature = PropertyMock(return_value=25.0)
        type(mock_dht).humidity = PropertyMock(return_value=60.0)
        temp, hum = dht11_mod.read()
        assert temp == 25.0
        assert hum == 60.0

    def test_returns_none_tuple_on_runtime_error(self, dht11_mod):
        """Transient sensor failures should yield (None, None)."""
        mock_dht = dht11_mod.dht
        type(mock_dht).temperature = PropertyMock(
            side_effect=RuntimeError("DHT read fail")
        )
        temp, hum = dht11_mod.read()
        assert temp is None
        assert hum is None


# ── is_alert() ────────────────────────────────────────────────────────────────


class TestIsAlert:
    """
    Thresholds are loaded from config.json at import time:
        dht11_temp_threshold     (default 40 °C)
        dht11_humidity_threshold (default 80 %)

    These tests patch dht11.read() directly to decouple from mock property
    quirks on the underlying DHT object.
    """

    def test_normal_readings_no_alert(self, dht11_mod):
        with patch.object(dht11_mod, "read", return_value=(25.0, 50.0)):
            assert dht11_mod.is_alert() is False

    def test_high_temperature_triggers_alert(self, dht11_mod):
        with patch.object(dht11_mod, "read", return_value=(42.0, 50.0)):
            assert dht11_mod.is_alert() is True

    def test_high_humidity_triggers_alert(self, dht11_mod):
        with patch.object(dht11_mod, "read", return_value=(25.0, 85.0)):
            assert dht11_mod.is_alert() is True

    def test_both_high_triggers_alert(self, dht11_mod):
        with patch.object(dht11_mod, "read", return_value=(45.0, 90.0)):
            assert dht11_mod.is_alert() is True

    def test_at_exact_threshold_triggers_alert(self, dht11_mod):
        """Boundary: values equal to threshold should trigger."""
        import config

        with patch.object(
            dht11_mod, "read",
            return_value=(float(config.dht11_temp_threshold), 50.0),
        ):
            assert dht11_mod.is_alert() is True

    def test_just_below_threshold_no_alert(self, dht11_mod):
        import config

        with patch.object(
            dht11_mod, "read",
            return_value=(
                config.dht11_temp_threshold - 0.1,
                config.dht11_humidity_threshold - 0.1,
            ),
        ):
            assert dht11_mod.is_alert() is False

    def test_failed_read_does_not_alert(self, dht11_mod):
        """A sensor read failure should not trigger a false positive."""
        with patch.object(dht11_mod, "read", return_value=(None, None)):
            assert dht11_mod.is_alert() is False

    def test_is_alert_returns_bool(self, dht11_mod):
        with patch.object(dht11_mod, "read", return_value=(25.0, 50.0)):
            result = dht11_mod.is_alert()
            assert isinstance(result, bool), (
                f"Expected bool, got {type(result).__name__}"
            )
