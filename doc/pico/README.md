
## Raspberry Pi PICO W documentation and code

This directory contains PicoW related code and documentation

### Contents

* README.md - this file
* Pico-ePaper-7.5.py - driver and demo for the 7.5" monochrome display
* Pico_ePaper_Code.zip - unaltered Waveshare pico code from their website 10/15/2024


### Vendor Documentation

* [product page](https://www.waveshare.com/7.5inch-e-paper-hat.htm)
* [picoW diagram](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)
* [driver board](https://www.waveshare.com/product/displays/e-paper/driver-boards/e-paper-driver-hat.htm)
* [driver board wiki](https://www.waveshare.com/wiki/E-Paper_Driver_HAT)
* [driver board schematic](https://files.waveshare.com/upload/8/8e/E-Paper_Driver_HAT.pdf)

At this writing, the v2.2 manual for the driver board has not been updated to v2.3 that they sell now.
It is important to read the disclaimers in red on the wiki link and to wire up the 'two' power related
pins correctly.  If you get the two power pins reversed the display will look terrible.  If you wire them
up correctly, the python demo code works fine.

* [v2.2 manual](https://files.waveshare.com/upload/8/8e/E-paper-driver-hat-user-manual.pdf)

