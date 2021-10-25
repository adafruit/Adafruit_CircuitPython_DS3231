Introduction
=============

.. image:: https://readthedocs.org/projects/adafruit-micropython-ds3231/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/ds3231/en/latest/
    :alt: Documentation Status

.. image :: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_DS3231/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_DS3231/actions/
    :alt: Build Status

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

.. image:: ../docs/_static/3013-01.jpg
    :alt: DS3231 Product Image

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-ds3231/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ds3231

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ds3231

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-ds3231

Usage Notes
===========

Basics
------

Of course, you must import the library to use it:

.. code:: python3

    import adafruit_ds3231
    import time

All the Adafruit RTC libraries take an instantiated and active I2C object
(from the ``board`` library) as an argument to their constructor. The way to
create an I2C object depends on the board you are using. For boards with labeled
SCL and SDA pins, you can:

.. code:: python3

    import board

Now, to initialize the I2C bus:

.. code:: python3

    i2c = board.I2C()  # uses board.SCL and board.SDA

Once you have created the I2C interface object, you can use it to instantiate
the RTC object:

.. code:: python3

    rtc = adafruit_ds3231.DS3231(i2c)

Date and time
-------------

To set the time, you need to set ``datetime`` to a ``time.struct_time`` object:

.. code:: python3

    rtc.datetime = time.struct_time((2017,1,9,15,6,0,0,9,-1))

After the RTC is set, you retrieve the time by reading the ``datetime``
attribute and access the standard attributes of a struct_time such as ``tm_year``,
``tm_hour`` and ``tm_min``.

.. code:: python3

    t = rtc.datetime
    print(t)
    print(t.tm_hour, t.tm_min)

Alarm
-----

To set the time, you need to set ``alarm1`` or ``alarm2`` to a tuple with a
``time.struct_time`` object and string representing the frequency such as "hourly":

.. code:: python3

    rtc.alarm1 = (time.struct_time((2017,1,9,15,6,0,0,9,-1)), "daily")

After the RTC is set, you retrieve the alarm status by reading the corresponding
``alarm1_status`` or ``alarm2_status`` attributes. Once True, set it back to False
to reset.

.. code:: python3

    if rtc.alarm1_status:
        print("wake up!")
        rtc.alarm1_status = False

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://circuitpython.readthedocs.io/projects/ds3231/en/latest/>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_DS3231/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
