#-----------------------------------------------------------
# minimal variant of weather.py to test screen compatibility
# this just puts the template on the screen
#
# note: for the 2-color display this needs to use the older
#       v4.0 version of the waveshare libs but the 3-color
#       still uses the original upstream (later) library
#-----------------------------------------------------------

# alphabetical order here so we can keep track
import csv
from   datetime import datetime
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


#---------------------------------------------------------------

def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    h_image = Image.new('1', (epd.width, epd.height), 255)
    screen_output_file = Image.open(os.path.join(picdir, image))
    h_image.paste(screen_output_file, (0, 0))
    epd.init()
    if config['twocolor_display']:
        epd.display(epd.getbuffer(h_image))
    else:
        h_red_image = Image.new('1', (epd.width, epd.height), 255)
        draw_red = ImageDraw.Draw(h_red_image)
        epd.display(epd.getbuffer(h_image), epd.getbuffer(h_red_image))
    time.sleep(2)
    epd.sleep()

    # TODO: should this be in the main program ?
    print('Sleeping for ' + str(sleep_seconds) +'.')
    time.sleep(sleep_seconds)

#---------------------------------------------------------------
# main() here
#---------------------------------------------------------------

picdir  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')

# write scratch files herre
tmpdir  = "/tmp"

# search lib folder for display driver modules
sys.path.append('lib')

# we'd also read the config file here.....
config = {}

###########################################################
# set these true/false to manually test the screen result #
###########################################################
                                                          #
config['twocolor_display'] = True                         #
lightning                  = False                        # 
total_rain                 = 23                           #
event                      = "test warning"               #
                                                          #
###########################################################



# use the correct module for the specified type of display
if config['twocolor_display']:
    from waveshare_epd import epd7in5_V2
    epd = epd7in5_V2.EPD()
else:
    from waveshare_epd import epd7in5b_V2
    epd = epd7in5b_V2.EPD()

# Set the fonts
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font23 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 23)
font25 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 25)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 160)

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

#Comment/Remove if using a 2 color screen
#TODO - this doesn't seem to matter based on testing
red  = 'rgb(255,0,0)'

#---------------------------------------------------------------

# Initialize and clear screen
print('Initializing and clearing screen.')
epd.init()
epd.Clear()

#---------------------------------------------------------------

# This is wrapped in a try/except block so we can catch
# keyboard interrupts and cleanly init/clear/sleep the
# display to try to prevent burn-in.  It is not perfect
# but catches most of the ^C interrupts gracefully enough

try:
    while True:

        template = Image.open(os.path.join(picdir, 'template.png'))
        draw = ImageDraw.Draw(template)

        #### overlay scratch data onto the image
        draw.text((65, 223),  "30.2" , font=font22,  fill=black)  # baro
        draw.text((65, 263),  "72"   , font=font22,  fill=black)  # precip_pct
        draw.text((35, 330),  "75"   , font=font50,  fill=black)  # temp_max
        draw.text((35, 395),  "50"   , font=font50,  fill=black)  # temp_min
        draw.text((360, 195), "66"   , font=font50,  fill=black)  # feels_like
        draw.text((365, 35),  "68"   , font=font160, fill=black)  # temp_current
        draw.text((370, 330), "78"   , font=font23,  fill=black)  # humidity
        draw.text((370, 383), "54"   , font=font23,  fill=black)  # dewpt
        draw.text((370, 435), "12"   , font=font23,  fill=black)  # wind
        draw.text((380, 22),  "1.23" , font=font23,  fill=black)  # total_rain
        draw.text((385, 263), event  , font=font23,  fill=black)  # event

        if total_rain > 0 or total_rain == 1000:
            train_image = Image.open(os.path.join(icondir, "totalrain.png"))
            template.paste(train_image, (330, 15))
            draw.text((380, 22), "l", font=font23, fill=black)
        try:
             if event != None:
                alert_image = Image.open(os.path.join(icondir, "warning.png"))
                template.paste(alert_image, (335, 255))
                draw.text((385, 263), event, font=font23, fill=black)
        except NameError:
            print('No Severe Weather')

        if lightning:
            draw.text((695, 330), 'Strikes', font=font22, fill=white)
            draw.text((685, 400), 'Distance', font=font22, fill=white)
            draw.text((683, 430), "m", font=font20, fill=white)  # distance
            draw.text((703, 360), "n", font=font20, fill=white)  # strikes
            strike_image = Image.open(os.path.join(icondir, "strike.png"))
            template.paste(strike_image, (605, 305))
        else:
            draw.text((627, 330), 'UPDATED', font=font35, fill=white)
            draw.text((627, 375), "12:34", font = font60, fill=white)  # HH:MM

        # Save the image for display as PN
        screen_output_file = os.path.join(tmpdir, 'screen_output.png')
        template.save(screen_output_file) # TODO: this should go to /tmp

        # Close the template file
        template.close()

        # write generated output file to screen
        write_to_screen(screen_output_file, 300)

except KeyboardInterrupt:
    print()
    print()
    print("#-----------------------------------")
    print("#       exiting on control-c        ")
    print("#    (this takes a few seconds)     ")
    epd.init()
    epd.Clear()
    epd.sleep()
    print("#          done                     ")
    print("#-----------------------------------")
    print()



