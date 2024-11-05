## weewx-epaper - weewx skin that generates data for waveshare epaper display

Copyright 2024 Vince Skahan

### Installation instructions:
This skin can be installed/uninstalled using the WeeWX extension installer.

#### 1. download the .zip file for this branch

`wget https://github.com/vinceskahan/vds-weewx-epaper-extension/archive/refs/heads/master.zip -O /var/tmp/weewx-epaper-extension.zip`

#### 2. install the extension with the WeeWX extension installer

For weewx 4.x:

`wee_extension --install /var/tmp/weewx-epaper-extension.zip`

For weewx 5.x:

`weectl extension install /var/tmp/weewx-epaper-extension.zip`

#### 3. restart weewx

`sudo systemctl restart weewx`


