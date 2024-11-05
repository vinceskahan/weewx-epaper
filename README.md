## WeeWX E-paper Weather Display

Display your WeeWX weather data and NWS alerts/forecasts on a 7.5" Waveshare e-paper display.

Note - actual good docs are TBD :-)

Raspberry Pi weather display using Waveshare e-paper 7.5 inch display, WeeWX Weather Station data, and Python3.

Sample output:
* [<img src="https://github.com/vinceskahan/Tempest-7.5-E-Paper-Display/blob/twocolor/doc/screen_output.png" width=40% height=40%>](link)

## Versions
* Version 0.1
    <ul>
	  <li>Initial Commit.</li>
	</ul>

## Setup
This project assumes you have a working WeeWX system with a linked in webserver.

1. Install the skin located under the docs directory here
2. Enable the SPI interface on your pi via the instructions from Waveshare (https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)_Manual#Enable_SPI_Interface). If not already enabled, this will require a one-time reboot of the pi.
3. Copy 'config.json.example' to 'config.json' and edit per the instructions therein.
4. To test, cd to the directory and run "python3 weather.py".  Hit Control-C to exit.
5. To interactively run in the background, run "bash runit".  You'll need to manually kill the process in this case.

## Partslist
* https://www.waveshare.com/7.5inch-e-paper-hat-b.htm -OR- https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT</li>
* Raspberry Pi ZeroW+, pi3, or later</li>
* SD card for the Pi at least 8 GB.</li>
* Power supply for the Pi.</li>
* 5 x 7 inch photo frame</li>
* Optional: 3D printer to print new back/mask for frame</li>

## Licensing
This licensing data is from the upstream projects and is here for reference only.
* Code licensed under [MIT License](http://opensource.org/licenses/mit-license.html)</li>
* Documentation licensed under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0)</li>

## Credits
See the 'CREDITS' file in the subdirectory for more details.
