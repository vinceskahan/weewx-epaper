#-----------------------------------------------------------
# quick utility to clear and sleep the epaper display
#
# This can (should?) be run from cron periodically to
# prevent burn-in.  Also can be used to clear the screen
# if the normal program has aborted for some reason
#
#-----------------------------------------------------------

# alphabetical order here so we can keep track
import csv
from   datetime import datetime
import datetime
from   io import BytesIO
import json
import os
from   pathlib import Path
from   PIL import Image,ImageDraw,ImageFont
import requests
import sys
import time
import traceback
import urllib.request

#-----------------------------------------------------------

def read_config_file(CONFIG):

    """
    Read the program's JSON config file

    input:  full pathname to read
    output: a 'config' struct

    """
    if not Path(CONFIG).is_file():
        print("ERROR - cannot find config file")
        sys.exit(1)
    else:
        with open(CONFIG) as file:
            config = json.load(file)
            file.close()
    return config

#---------------------------------------------------------------
# main() here
#---------------------------------------------------------------

# read the config file
config = read_config_file('config.json')
if 'config' in config['debug']:
    print(config)

# search lib folder for display driver modules
sys.path.append('lib')

# use the correct module for the specified type of display
if config['twocolor_display']:
    from waveshare_epd import epd7in5_V2
    epd = epd7in5_V2.EPD()
else:
    from waveshare_epd import epd7in5b_V2
    epd = epd7in5b_V2.EPD()

print('Initializing screen...')
epd.init()
print('Clearing screen...')
epd.Clear()
print('Sleeping screen...')
epd.sleep()
print('Done...')


