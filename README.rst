Introduction
============

The datasheet for the DS3231 explains that this part is an
"Extremely Accurate I²C-Integrated RTC/TCXO/Crystal". And,
hey, it does exactly what it says on the tin! This Real Time
Clock (RTC) is the most precise you can get in a small, low
power package.

Most RTCs use an external 32kHz timing crystal that is used
to keep time with low current draw. And that's all well and
good, but those crystals have slight drift, particularly when
the temperature changes (the temperature changes the oscillation
frequency very very very slightly but it does add up!) This
RTC is in a beefy package because the crystal is inside the
chip! And right next to the integrated crystal is a temperature
sensor. That sensor compensates for the frequency changes by
adding or removing clock ticks so that the timekeeping stays
on schedule.

This is the finest RTC you can get, and now we have it in a
compact, breadboard-friendly breakout. With a coin cell
plugged into the back, you can get years of precision
timekeeping, even when main power is lost. Great for
datalogging and clocks, or anything where you need to
really know the time.

.. image:: 3013-01.jpg


Implementation Details
=======================

Background
----------

This page contains the details of the functions, classes, and methods
available in the DS3231 library.

The DS3231 library consists of three major sections:

#. Functions
#. The base class _BaseRTC
#. The subclass DS1307

Functions
---------

The only library functions of which you need to be aware of for the
DS1307 are datetime_tuple() and alarm_tuple().

The first is the function that creates an object
you use to set the clock time. It takes eight arguments and returns a
datetimetuple object containing the new time settings. The arguments are
positional rather than keyword arguments. They are, in order:

* Year (4-digit)
* Month (2-digit)
* Day of the month (2-digit)
* Day of the week (1 digit, 0 = Sunday)
* Hour (24 hour clock, 2-digit)
* Minute (2-digit)
* Seconds (2-digits)
* The digit 0 (representing milliseconds, which are not supported by this RTC)

The second is the function that returns an alarmtuple structure to set the
alarm on the RTC. It takes four arguments:

* Day of the week
* Day of the month
* hour
* minute

See the section, below, on usage for examples.

Class Methods
-------------

Here are the important class methods for you to know:

* datetime() - sets or returns the RTC clock time
* alarm_time() - sets or returns the current alarm setting
* _register() - returns the contents of a register in the RTC chip
* stop() - suspends RTC operation or, if the argument is None, returns the
  current setting.
* lost_power() - returns true or false depending on whether the board has
  lost power. Passing the value "False" will reset the flag.
* alarm() - returns the alarm state (True or False). Passing False as the
  argument will reset the flag.
* interruptEnable() - determines whether an alarm generates an interrupt on the
  INT/SQW pin

Usage Notes
===========

Of course, you must import the library to use it:

   import machine

   import adafruit_ds3231

All the Adafruit RTC libraries take an instantiated and active I2C object
(from the machine library) as an argument to their constructor. The way to
create an I2C object depends on the board you are using. If you are using the
ATSAMD21-based board, like the Feather M0, you **must** initialize the object
after you create it:

   myI2C = machine.I2C(machine.Pin('SCL'), machine.Pin('SDA'))

   myI2C.init()

If you are using the ESP8266-based boards, however, you do not need to
init() the object after creating it:

   myI2C = machine.I2C(machine.Pin(5), machine.Pin(4))

Once you have created the I2C interface object, you can use it to instantiate
the RTC object:

   rtc = adafruit_ds3231.DS3231(myI2C)

To set the time, you need to pass datetime() a datetimetuple object:

   newTime = adafruit_ds3231.datetime_tuple(2016,11,18,6,9,36,0,0)

   rtc.datetime(newTime)

After the RTC is set, you retrieve the time by calling the datetime() method
without any arguments.

   curTime = rtc.datetime()

The DS3231 supports an alarm function. You set the alarm very similarly to
the way you set the datetime.

   newAlarm = adafruit_ds3231.alarm_tuple(6,18,10,41)

   rtc.alarm_time(newAlarm)

Many more details can be found in the Docs/_build directory.
