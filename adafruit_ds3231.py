# The MIT License (MIT)
#
# Copyright (c) 2016 Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ds3231` - DS3231 Real Time Clock module
=================================================
CircuitPython library to support DS3231 Real Time Clock (RTC).

This library supports the use of the DS3231-based RTC in CircuitPython.

Author(s): Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.

Implementation Notes
--------------------

**Hardware:**

* Adafruit `DS3231 Precision RTC FeatherWing <https://www.adafruit.com/products/3028>`_
  (Product ID: 3028)

* Adafruit `DS3231 RTC breakout <https://www.adafruit.com/products/3013>`_ (Product ID: 3013)
* Adafruit `ChronoDot - Ultra-precise Real Time Clock -
  v2.1 <https://www.adafruit.com/products/255>`_ (Product ID: 3013)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the ESP8622 and M0-based boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

**Notes:**

#. Milliseconds are not supported by this RTC.
#. Datasheet: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

"""
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register import i2c_bit
from adafruit_register import i2c_bcd_alarm
from adafruit_register import i2c_bcd_datetime

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DS3231.git"

# pylint: disable-msg=too-few-public-methods
class DS3231:
    """Interface to the DS3231 RTC."""

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

    def __init__(self, i2c):
        self.i2c_device = I2CDevice(i2c, 0x68)

    @property
    def datetime(self):
        """Gets the current date and time or sets the current date and time
        then starts the clock."""
        return self.datetime_register

    @datetime.setter
    def datetime(self, value):
        self.datetime_register = value
        self.disable_oscillator = False
        self.lost_power = False
