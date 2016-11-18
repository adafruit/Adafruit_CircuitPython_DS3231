
""" MicroPython library to support DS3231 Real Time Clock (RTC).

This library supports the use of the DS3231-based RTC in MicroPython. It
contains a base RTC class used by all Adafruit RTC libraries. This base
class is inherited by the chip-specific subclasses.

Functions are included for reading and writing registers and manipulating
datetime objects.

Author(s): Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.
Date: November 2016
Affiliation: Adafruit Industries

Implementation Notes
--------------------

**Hardware:**

* Adafruit `Feather HUZZAH ESP8266 <https://www.adafruit.com/products/2821>`_ (Product ID: 2821)
* Adafruit `Feather M0 Adalogger <https://www.adafruit.com/products/2796>`_  (Product ID: 2796)
* Adafruit `Arduino Zero <https://www.adafruit.com/products/2843>`_ (Product ID: 2843)
* Pycom LoPy
* Adafruit `DS3231 RTC breakout <https://www.adafruit.com/products/3013>`_ (Product ID: 3013)

**Software and Dependencies:**

* MicroPython firmware for the ESP8622, which can be obtained from:

https://micropython.org/download/#esp8266

* MicroPython firmware for the M0-based boards, which can be obtained from:

https://github.com/adafruit/micropython/releases

* ucollections library
* utime library

**Notes:**

#. Milliseconds are not supported by this RTC.
#. The data sheet for the DS3231 can be obtained from.
#. mpy files automatically generated.

https://datasheets.maximintegrated.com/en/ds/DS3231.pdf

"""

##############################################################################
# Credits and Acknowledgements:
#        Original code written by Radomir Dopieralski. See LICENSE file.
##############################################################################


##############################################################################
# Imports
##############################################################################

try:
	import os
except ImportError:
	import uos as os

osName = os.uname()[0]
bootMicro = False
if 'samd21' == osName:
	bootMicro = True
if 'esp8266' == osName:
	bootMicro = True
if 'LoPy' == osName:
	bootMicro = True
if 'WiPy' == osName:
	bootMicro = True
if 'pyboard' == osName:
	bootMicro = True

if bootMicro:
	import ucollections
	import utime
else:
	import collections as ucollections
	import time as utime


##############################################################################
# Globals and constants
##############################################################################

DateTimeTuple = ucollections.namedtuple("DateTimeTuple", ["year", "month",
    "day", "weekday", "hour", "minute", "second", "millisecond"])
AlarmTuple = ucollections.namedtuple("AlarmTuple", ["day", "hour",
    "minute", "seconds"])


##############################################################################
# Functions
##############################################################################

def datetime_tuple(year, month, day, weekday=0, hour=0, minute=0,
                   second=0, millisecond=0):
    """Return individual values converted into a data structure (a tuple).

    **Arguments:**

    * year - The year (four digits, required, no default).
    * month - The month (two digits, required, no default).
    * day - The day (two digits, required, no default).
    * weekday - The day of the week (one digit, optional, default zero).
    * hour - The hour (two digits, 24-hour format, optional, default zero).
    * minute - The minute (two digits, optional, default zero).
    * second - The second (two digits, optional, default zero).
    * millisecond - Milliseconds (not supported, default zero).

    """
    return DateTimeTuple(year, month, day, weekday, hour, minute,
                         second, millisecond)

# Only supports day at this time, not weekday.
def alarm_tuple(day, hour, minute, seconds):
    """Return data structure for writing DS3231 alarm registers.

    **Arguments:**

    * day - The day of the month for the alarm (required, no default)
    * hour - The hour of the alarm (required, no default)
    * minute - The minute for the alarm (required, no default)
    * seconds - The sedons for the alarm (required, no default)

    """
    return AlarmTuple(day, hour, minute, seconds)

def _bcd2bin(value):
    """Convert binary coded decimal to Binary

    **Arguments:**

    * value - the BCD value to convert to binary (required, no default)

    """
    return value - 6 * (value >> 4)


def _bin2bcd(value):
    """Convert a binary value to binary coded decimal.

    **Arguments:**

    * value - the binary value to convert to BCD. (required, no default)

    """
    return value + 6 * (value // 10)


def tuple2seconds(datetime):
    """Convert a datetime tuple to seconds since the epoch.

    **Arguments:**

    * datetime - a datetime tuple containing the date and time to convert.
      (required, no default)

    """
    return utime.mktime((datetime.year, datetime.month, datetime.day,
        datetime.hour, datetime.minute, datetime.second, datetime.weekday, 0))


def seconds2tuple(seconds):
    """Convert seconds since the epoch into a datetime structure.

    **Arguments:**

    * seconds - the value to convert. (required, no default)

    """
    year, month, day, hour, minute, second, weekday, _yday = utime.localtime()
    return DateTimeTuple(year, month, day, weekday, hour, minute, second, 0)


##############################################################################
# Classes and methods
##############################################################################

class _BaseRTC:
    """ Provide RTC functionality common across all Adafruit RTC products.

    This is the parent class inherited by the chip-specific subclasses.

    **Methods:**

    * __init__ - constructor (must be passed I2C interface object)
    * _register - read and write registers
    * _flag - return or set flag bits in registers

    """
    def __init__(self, i2c, address=0x68):
        """Base RTC class constructor.

        **Arguments:**

        * i2c - an existing I2C interface object (required, no default)
        * address - the hex i2c address for the DS3231 chip (default 0x68).

        """
        self.i2c = i2c
        self.address = address

    def _register(self, register, buffer=None):
        """Base RTC class register method to set or read a register value.

        **Arguments:**

        * register - Hex address of the register to be manipulated. (required)
        * buffer - Data to be written to the register location, or None
          if the register is to be read.

        """
        if buffer is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        self.i2c.writeto_mem(self.address, register, buffer)

    def _flag(self, register, mask, value=None):
        """Set or return a bitwise flag setting.

        **Arguments:**

        * register - Hex address of the register to be used. (required)
        * mask - Binary bitmask to extract or write specific bits. (required)
        * value - Data to write into the flag register. If None, the method
        * returns the flag(s). If set, it is written to the register (using the
          mask parameter). (optional, default None)

        """
        data = self._register(register)
        if value is None:
            return bool(data & mask)
        if value:
            data |= mask
        else:
            data &= ~mask
        self._register(register, bytearray((data,)))


class DS3231(_BaseRTC):
    """Subclass that implements DS3231-specific methods.

    ***Methods:***

    * __init__ - Overloaded constructor.
    * init - Local scope initialization, called from __init__().
    * dateime - Set or return the current RTC time/calendar values.
    * alarm_time - Set or return the current alarm one time setting.
    * lost_power - True if the RTC has lost power and switched to battery.
    * alarm - True if the alarm conditions have been met. Set to False to
      clear interrupt and alarm.
    * interruptEnable - Enable the interrupt pin action on alarm.
    * stop - Stop transmitting data on I2C and freeze registers.
    * setAlarmField - Sets the internal alarmField to the passed value.

    """
    _CONTROL_REGISTER = 0x0e
    _STATUS_REGISTER = 0x0f
    _DATETIME_REGISTER = 0x00
    _ALARM_REGISTER = 0x07
    _SQUARE_WAVE_REGISTER = 0x0e

    def __init__(self, *args, **kwargs):
        """Overloaded _BaseRTC constructor for DS3231-specific arguments."""
        super().__init__(*args, **kwargs)
        self.init()

    def init(self):
        """Initializes flag for alarm setting.

        **Arguments:**

        * none

        """
        self.alarmField = True

    # def datetime(self, datetime=None):
    #    if datetime is not None:
    #        status = self._register(self._STATUS_REGISTER) & 0b01111111
    #        self._register(self._STATUS_REGISTER, bytearray((status,)))
    #    return super().datetime(datetime)


    def datetime(self, datetime=None):
        """Set or return current time and calendar values.

        **Arguments:**

        * datetime - a datetime_tuple structure with data, or None. If None,
          returns the current datetime, else sets the RTC.

        """
        buffer = bytearray(7)
        if datetime is None:
            self.i2c.readfrom_mem_into(self.address, self._DATETIME_REGISTER,
                                       buffer)
            return datetime_tuple(
                year=_bcd2bin(buffer[6]) + 2000,
                month=_bcd2bin(buffer[5]),
                day=_bcd2bin(buffer[4]),
                weekday=_bcd2bin(buffer[3]),
                hour=_bcd2bin(buffer[2]),
                minute=_bcd2bin(buffer[1]),
                second=_bcd2bin(buffer[0]),
            )
        status = self._register(self._STATUS_REGISTER) & 0b01111111
        self._register(self._STATUS_REGISTER, bytearray((status,)))
        datetime = datetime_tuple(*datetime)
        buffer[0] = _bin2bcd(datetime.second)
        buffer[1] = _bin2bcd(datetime.minute)
        buffer[2] = _bin2bcd(datetime.hour)
        buffer[3] = _bin2bcd(datetime.weekday)
        buffer[4] = _bin2bcd(datetime.day)
        buffer[5] = _bin2bcd(datetime.month)
        buffer[6] = _bin2bcd(datetime.year - 2000)
        self._register(self._DATETIME_REGISTER, buffer)

    def alarm_time(self, alarmTime=None):
        """Sets or returns the current alarm time.

        **Arguements:**

        * alarmTime - alarmtime_tuple structure containing the new alarm
          time, which sets the alarm, or None, which returns the current value.

        """
        buffer = bytearray(4)
        if alarmTime is None:
            self.i2c.readfrom_mem_into(self.address, self._ALARM_REGISTER,
                                      buffer)

            day = _bcd2bin(buffer[3] & 0x1F)
            hour = _bcd2bin(buffer[2] & 0x3F)
            minute = _bcd2bin(buffer[1] & 0x7F)
            seconds = _bcd2bin(buffer[0] & 0x7F)

            return alarm_tuple(day, hour, minute, seconds)

        alarmTime = alarm_tuple(*alarmTime)

        # DS3231-specific bitfields in the alarm register
        buffer[0] = (_bin2bcd(alarmTime.seconds)
                     if alarmTime.seconds is not None else 0x00)
        buffer[1] = (_bin2bcd(alarmTime.minute)
                     if alarmTime.minute is not None else 0x00)
        buffer[2] = (_bin2bcd(alarmTime.hour)
                     if alarmTime.hour is not None else 0x00)
        buffer[3] = (_bin2bcd(alarmTime.day)
                     if alarmTime.day is not None else 0x00)
        self._register(self._ALARM_REGISTER, buffer)


    def lost_power(self):
        """Return true if the RTC has lost power."""
        return self._flag(self._STATUS_REGISTER, 0b10000000)

    def alarm(self, value=None):
        """Clears or returns the alarm condition.

        **Arguments:**

        * value - False to clear the alarm, None to return the current value.
          (optional, default None)

        """
        # Change mask to 0b00000011 to check alarms one and two.
        # Set/return the alarm flag
        return self._flag(self._STATUS_REGISTER, 0b00000001, value)

    def interruptEnable(self, value=True):
        """Sets or unsets the interrupt pin enable for alarms.

        **Arguments:**

        * value - A boolean that enables or disables the alarm interrupt.
          (optional, default True)

        """
        self._flag(self._CONTROL_REGISTER, 0b00000001, True)
		# self._flag(self._CONTROL_REGISTER, 0b00000101, 0x5)

    def stop(self, value=None):
        """Stops the RTC from transmitting data on I2C and freezes registers.

        **Arguments:**

        * value - True to stop the RTC, None to return current value. (optional,
          default None)

        """
        return self._flag(self._CONTROL_REGISTER, 0b10000000, value)

    def setAlarmField(self, value=True):
        """Set internal alarmField value.

        **Arguments:**

        * value - Boolean value to set or unset the alarmField value.
          (optional, default True)
        """
        self.alarmField = value
