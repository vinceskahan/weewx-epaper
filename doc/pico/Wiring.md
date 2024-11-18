
## How to wire the display to a pico

The Waveshare documentation is sometimes ancient, very skeletal, and a bit plagued by bad or incomplete translations to English.  Here is how to wire the 7.5" display to the pico in order to run the Waveshare python demo.


### Using the 9-pin cable

The 'e-Paper Driver HAT' board can be connected via the included 9-pin cable.

```
Colors below are on the 9-pin that came with the v2.3 board....

brown  PWR  to pico pin 39 VSYS
purple BUSY to pico pin 17 GP13
white  RST  to pico pin 16 GP12
green  DC   to pico pin 11 GP8
orange CS   to pico pin 12 GP9
yellow CLK  to pico pin 14 GP10
blue   DIN  to pico pin 15 GP11
black  GND  to pico pin 38 GND
red    VCC  to pico pin 36 3V3(OUT)
```

