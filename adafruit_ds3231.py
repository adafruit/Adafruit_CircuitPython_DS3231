# SPDX-FileCopyrightText: 2016 Philip R. Moyer for Adafruit Industries
# SPDX-FileCopyrightText: 2016 Radomir Dopieralski for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ds3231`
=================================================
CircuitPython library to support DS3231 Real Time Clock (RTC).

This library supports the use of the DS3231-based RTC in CircuitPython.

Author(s): Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.

Implementation Notes
--------------------

**Hardware:**

* `Adafruit DS3231 Precision RTC FeatherWing
  <https://www.adafruit.com/products/3028>`_ (Product ID: 3028)

* `Adafruit DS3231 RTC breakout
  <https://www.adafruit.com/products/3013>`_ (Product ID: 3013)

* `Adafruit ChronoDot - Ultra-precise Real Time Clock - v2.1
  <https://www.adafruit.com/products/255>`_ (Product ID: 255)


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

* Adafruit's Register library:
  https://github.com/adafruit/Adafruit_CircuitPython_Register


**Notes:**

#. Milliseconds are not supported by this RTC.
#. Datasheet: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

"""
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register import i2c_bit
from adafruit_register import i2c_bits
from adafruit_register import i2c_bcd_alarm
from adafruit_register import i2c_bcd_datetime

try:
    # Used only for typing
    import typing  # pylint: disable=unused-import
    from busio import I2C
    from time import struct_time
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DS3231.git"

# pylint: disable-msg=too-few-public-methods
class DS3231:
    """Interface to the DS3231 RTC.

    :param ~busio.I2C i2c: The I2C bus the device is connected to

    **Quickstart: Importing and using the device**

        Here is an example of using the :class:`DS3231` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import time
            import board
            import adafruit_ds3231

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            rtc = adafruit_ds3231.DS3231(i2c)

        Now you can give the current time to the device.

        .. code-block:: python

            t = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
            rtc.datetime = t

        You can access the current time accessing the :attr:`datetime` attribute.

        .. code-block:: python

            current_time = rtc.datetime

    """

    lost_power = i2c_bit.RWBit(0x0F, 7)
    """True if the device has lost power since the time was set."""

    disable_oscillator = i2c_bit.RWBit(0x0E, 7)
    """True if the oscillator is disabled."""

    datetime_register = i2c_bcd_datetime.BCDDateTimeRegister(0x00)
    """Current date and time."""

    alarm1 = i2c_bcd_alarm.BCDAlarmTimeRegister(0x07)
    """Alarm time for the first alarm."""

    alarm1_interrupt = i2c_bit.RWBit(0x0E, 0)
    """True if the interrupt pin will output when alarm1 is alarming."""

    alarm1_status = i2c_bit.RWBit(0x0F, 0)
    """True if alarm1 is alarming. Set to False to reset."""

    alarm2 = i2c_bcd_alarm.BCDAlarmTimeRegister(0x0B, has_seconds=False)
    """Alarm time for the second alarm."""

    alarm2_interrupt = i2c_bit.RWBit(0x0E, 1)
    """True if the interrupt pin will output when alarm2 is alarming."""

    alarm2_status = i2c_bit.RWBit(0x0F, 1)
    """True if alarm2 is alarming. Set to False to reset."""

    # pylint: disable=unexpected-keyword-arg
    _calibration = i2c_bits.RWBits(8, 0x10, 0, 1, signed=True)

    _temperature = i2c_bits.RWBits(
        10, 0x11, 6, register_width=2, lsb_first=False, signed=True
    )
    # pylint: enable=unexpected-keyword-arg

    _busy = i2c_bit.ROBit(0x0F, 2)
    _conv = i2c_bit.RWBit(0x0E, 5)

    def __init__(self, i2c: I2C) -> None:
        self.i2c_device = I2CDevice(i2c, 0x68)

    @property
    def datetime(self) -> struct_time:
        """Gets the current date and time or sets the current date and time
        then starts the clock."""
        return self.datetime_register

    @datetime.setter
    def datetime(self, value: struct_time) -> None:
        self.datetime_register = value
        self.disable_oscillator = False
        self.lost_power = False

    @property
    def temperature(self) -> float:
        """Returns the last temperature measurement.  Temperature is updated
        only every 64 seconds, or when a conversion is forced."""
        return self._temperature / 4

    def force_temperature_conversion(self) -> float:
        """Forces a conversion and returns the new temperature"""
        while self._busy:
            pass  # Wait for any normal in-progress conversion to complete
        self._conv = True
        while self._conv:
            pass  # Wait for manual conversion request to complete
        return self.temperature

    @property
    def calibration(self) -> int:
        """Calibrate the frequency of the crystal oscillator by adding or
        removing capacitance.  The datasheet calls this the Aging Offset.
        Calibration values range from -128 to 127; each step is approximately
        0.1ppm, and positive values decrease the frequency (increase the
        period).  When set, a temperature conversion is forced so the result of
        calibration can be seen directly at the 32kHz pin immediately"""
        return self._calibration

    @calibration.setter
    def calibration(self, value: int) -> None:
        self._calibration = value
        self.force_temperature_conversion()
