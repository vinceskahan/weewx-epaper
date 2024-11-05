<h1>Tempest E-paper Weather Display</h1>

<p>
Note: this branch has my mods to try to make this cool program more configurable and extensible, using weeWX for weather and NWS for alerts/forecasts.

For weewx users, install the weewx-json skin to generate JSON-formatted data when your weewx reports are generated.  In that case you want to specify the path to its generated "weewx.json" file in the data_url item in config.json here.  It is untested whether a file:///somepath/here/weewx.json url will work or not.  More typical http://something/weewx.json url is tested and works ok here.

See the config.json.example file for how to install it.  The bash script "runit" will fire it up in the background, nohupped, with debugging logs to /tmp which is typically tmpfs so your SD card should be protected from too many writes.  One installed, no actual writes will be done.

This variant uses a somewhat older version of the waveshare libs for the 2-color greyscale screen (included).

Note - actual good docs are TBD :-)

<p>

<hr>
<h2> upstream readme follows </h2>
<hr>

<br>
  Raspberry Pi weather display using Waveshare e-paper 7.5 inch display, Tempest Weather Station data, and Python.
<img src="https://github.com/OG-Anorine/Tempest-7.5-E-Paper-Display/blob/master/photos/IMG_6648.jpeg" width=40% height=40%>
<br>
<img src="https://github.com/OG-Anorine/Tempest-7.5-E-Paper-Display/blob/master/photos/IMG_6607.jpeg" width=40% height=40%>
<h1>Versions</h1>
  <h2>Version 1.0</h2>
    <ul>
	  <li>Initial Commit.</li>
	</ul>

<h1>Setup</h1>
  <ol type="1">
    <li>Assuming you have a Pi of your choice loaded, you will need to setup the e-paper display per the instructions from WaveShare: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)_Manual#Working_With_Raspberry_Pi.  *Note: these instructions are for tthe 3 color screen which I am using.  I have included comments in the code to change it back to the 2 color if desired.</li>
    <li>Open 'weather.py' and replace **Station ID here** with you station ID (Log into tempestwx.com - after successful login your station id will be listed at the end of the URL: https://tempestwx.com/station/XXXXXX) and **Token Here** with your API key (Create authorization at https://tempestwx.com/settings/tokens).</li>
    <li>Get your State/County ID from NSW to populate Watch/Warning data.  I have not found a great way to get this data other than using a multi-step process.  1. Go to https://www.weather.gov and enter your ZIP code on the left.  2. After the locaiton loads, click on "Get detailed info" 3. Select your city if needed 4. Get the coordinates out of the URL - these will be plugged into the API via browser of your choice: https://api.weather.gov/points/[start,end] - read through the data and look for "county": at the end of the JSON response.  This is your county code to plug into the Python code.  </li>
    <li>Create a script in your home directory that contains 2 commands. cd /home/[username]/Tempest-7.5-E-Paper-Display and sudo python weather.py - each on their own line.  Name this file something like startup.sh.  You will then need to chmod 755 [filename].sh to allow it to execute./</li>
    <li>Create 2 cronjobs in the root crontab.  1. @reboot /home/[username]/[filenamefromabovestep].sh - and 2. 30 3 * * * reboot - the first number represents minutes, the second the hour.  Reboot the Pi at a time of your choosing, this will refresh the screen to prevent burn-in. </li>
  </ol>
<br> 

# Note 
The storm data on this build is dynamic.  Rain totals, severe weather alerts, and lightning strike data only show up when it is present.  This is intentional to reduce clutter on the screen.

<b>Storm data:</b>
<br>
<img src="https://github.com/OG-Anorine/Tempest-7.5-E-Paper-Display/blob/master/photos/storm.png"> 
<br>
<b>Normal:</b>
<br>
<img src="https://github.com/OG-Anorine/Tempest-7.5-E-Paper-Display/blob/master/photos/no_storm.png"> 
<br>
<br>
If you are not using a 7.5 inch Version 2b display, you will want to replace 'epd7in5b_V2.py' in the 'lib' folder with whichever one you have from https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd<br>
Fairly extensive adjustments will have to be made for other sized screens.

Optional items - there is code embedded that at a gust of 10MPH (at time of refresh) the current weather status will update to "IT HECKIN WIMDY" meme.  This was a nod to the Mrs who loves the meme, but by no means is required to remain.  THis section of code can easily be commented out and the windy.png icon replaced.  Simply remove windy.png and rename windy2.png to windy.png.  

# Parts
<ul>
  <li>https://www.waveshare.com/7.5inch-e-paper-hat-b.htm -OR- https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT</li>
  <li>Raspberry Pi ZeroW+</li>
  <li>SD card for the Pi at least 8 GB.</li>
  <li>Power supply for the Pi.</li>
  <li>5 x 7 inch photo frame</li>
  <li>Optional: 3D printer to print new back/mask for frame</li>
</ul>



<h1>Licensing</h1>
  <ul>
    <li>Code licensed under [MIT License](http://opensource.org/licenses/mit-license.html)</li>
    <li>Documentation licensed under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0)</li>
  <ul>
