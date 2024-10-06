#-------------------------------------------------------
# this is modified to use v4.0 of the waveshare libs
# which is older than the ones we started with here
#-------------------------------------------------------

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

#-----------------------------------------------------------

def read_config_file(CONFIG):
    if not Path(CONFIG).is_file():
        print("ERROR - cannot find config file")
        sys.exit(1)
    else:
        with open(CONFIG) as file:
            config = json.load(file)
            file.close()
    return config

#-----------------------------------------------------------

# test function to get 'anything' to the screen
def write_test_info(image, sleep_seconds):
    print('writing test info to screen')
    h_image = Image.new('1', (epd.width, epd.height), 255)

    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.init()
    epd.Clear()
    epd.init_fast()
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, 0), 'hello world', font = font20, fill = 0)
    draw.text((10, 20), '7.5inch e-Paper', font = font20, fill = 0)
    draw.text((150, 0), u'微雪电子', font = font20, fill = 0)
    draw.line((20, 50, 70, 100), fill = 0)
    draw.line((70, 50, 20, 100), fill = 0)
    draw.rectangle((20, 50, 70, 100), outline = 0)
    draw.line((165, 50, 165, 100), fill = 0)
    draw.line((140, 75, 190, 75), fill = 0)
    draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    draw.rectangle((80, 50, 130, 100), fill = 0)
    draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)
    epd.Clear()

    epd.sleep()
    print('sleeping for ' + str(sleep_seconds) + '.')
    time.sleep(sleep_seconds)

#-----------------------------------------------------------

# define funciton for writing image and sleeping for 5 min.
def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    # Write to screen
    h_image = Image.new('1', (epd.width, epd.height), 255)

    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.init()

    if config['twocolor_display']:
        epd.display(epd.getbuffer(h_image))
    else:
        h_red_image = Image.new('1', (epd.width, epd.height), 255)  # 250*122
        draw_red = ImageDraw.Draw(h_red_image)
        epd.display(epd.getbuffer(h_image), epd.getbuffer(h_red_image)) #Comment/Remove from the comma on if using a 2 color screen

    # Sleep
    time.sleep(2)
    epd.sleep()

    # TODO: this should be in the main program
    print('Sleeping for ' + str(sleep_seconds) +'.')
    time.sleep(sleep_seconds)

#-----------------------------------------------------------

# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source +' ERROR', font=font50, fill=black)
    draw.text((100, 300), 'Retrying in 30 seconds', font=font22, fill=black)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font = font50, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(picdir, error_image_file)) # TODO: this should go to /tmp
    # Close error image
    error_image.close()
    # Write error to screen
    if config['debug_screen'] == "True":
        write_test_info(error_image_file, 30)
    else:
        write_to_screen(error_image_file, 30)

#-----------------------------------------------------------
# main() here
#-----------------------------------------------------------

config = read_config_file('config.json')

picdir  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')

# assemble some url we will use below
current_conditions_url = 'https://swd.weatherflow.com/swd/rest/better_forecast?station_id=' + config['station_id'] \
                        + '&units_temp=f&units_wind=mph&units_pressure=inhg&units_precip=in&units_distance=mi&token=' + config['api_token']

alerts_url = "https://api.weather.gov/alerts/active?zone=" + config['alerts_zone']

# search lib folder for display driver modules
sys.path.append('lib')

# use the correct module for the specified type of display
if config['twocolor_display']:
    from waveshare_epd import epd7in5_V2
    epd = epd7in5_V2.EPD()
else:
    from waveshare_epd import epd7in5b_V2
    epd = epd7in5b_V2.EPD()

# Set the fonts
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

#-----------------------------------------------------------

# Initialize and clear screen
print('Initializing and clearing screen.')
epd.init()
epd.Clear()

#-----------------------------------------------------------

# This is wrapped in a try/except block so we can catch
# keyboard interrupts and cleanly init/clear/sleep the
# display to try to prevent burn-in.  It is not perfect
# but catches most of the ^C interrupts gracefully enough

try:
    while True:

        #--------------------------------
        # connect to the Tempest WX API
        #--------------------------------

        # Ensure there are no errors with connection
        error_connect = True
        while error_connect == True:
            try:
                # HTTP request
                print('Attempting to connect to Tempest WX.')
                response = requests.get(current_conditions_url)
                print('Connection to Tempest WX successful.')
                error_connect = None
            except:
                # Call function to display connection error
                print('Connection error.')
                display_error('CONNECTION')
                # TODO: shouldn't we sleep before trying again ?

        #--------------------------------
        # get Tempest WX current conditions
        #--------------------------------

        error = None
        while error == None:
            # Check status of code request
            if response.status_code == 200:
                print('JSON pull from Tempest WX successful.')
                # get data in json format
                f = urllib.request.urlopen(current_conditions_url)
                wxdata = json.load(f)
                f.close()

                # get current conditions
                try:
                    current = wxdata['current_conditions']
                except:
                    #TODO: should this display_error ?
                    print("no current conditions - exiting...")
                    sys.exit(0)

                #--------------------------------
                # decode the current conditions
                #--------------------------------

                # TODO: this should be a decode_current_conditions(current) routine
                # TODO: should each element be in a try/except block just.in.case. ?
                temp_current = current['air_temperature']
                feels_like   = current['feels_like']
                humidity     = current['relative_humidity']
                dewpt        = current['dew_point']
                wind         = current['wind_avg']
                windcard     = current['wind_direction_cardinal']
                gust         =  current['wind_gust']
                weather      = current['conditions']
                report       = current['conditions']
                if report == 'Thunderstorms Possible':
                    report = 'T-Storms Possible'
                baro         = current['sea_level_pressure']
                trend        = current['pressure_trend']
                # get icon url - manually override for wind > 10mph
                icon_code    = current['icon']
                if icon_code != 'thunderstorm' and icon_code != 'snow' and icon_code != 'sleet' and icon_code != 'rainy' and gust >= 10:
                    icon_code = 'windy'
                else:
                    icon_code = current['icon']
                try:
                    strikesraw = current['lightning_strike_count_last_3hr']
                except:
                    strikesraw = 0
                strikes       = f"{strikesraw:,}"

                # Lightning distance message
                try:
                    lightningdist = current['lightning_strike_last_distance_msg']
                except:
                    lightningdist = 0

                # get daily forcast for today
                daily = wxdata['forecast']['daily'][0]

                # get daily precip percentage forecast and current accumulation
                daily_precip_percent = daily['precip_probability']
                try:
                    total_rain = current['precip_accum_local_day']
                except:
                    total_rain = 0
                try:
                    rain_time = current['precip_minutes_local_day']
                except:
                    rain_time = 0
                if rain_time > 0 and total_rain <= 0:
                    total_rain = 1000

                # current and daily min and max temp
                daily_temp   = current['air_temperature']
                temp_max     = daily['air_temp_high']
                temp_min     = daily['air_temp_low']
                sunriseepoch = daily['sunrise']
                sunsetepoch  = daily['sunset']

                # convert epoch to readable time
                sunrise = datetime.fromtimestamp(sunriseepoch)
                sunset  = datetime.fromtimestamp(sunsetepoch)

                #--------------------------------
                # get and decode any NWS alerts
                #--------------------------------

                # Get Severe weather data from NWS
                if config['debug'] == "True":
                    print("trying to get weather alerts")
                response = requests.get(alerts_url)
                nws = response.json()
                if config['debug_nws'] == "True":
                    print("    done - the following is the payload")
                    print(nws)
                try:
                    alert    = nws['features'][int(0)]['properties']
                    event    = alert['event']
                    urgency  = alert['urgency']
                    severity = alert['severity']
                except IndexError:
                    alert    = None
                if alert != None and (event.endswith('Warning') or event.endswith('Watch')):
                    string_event = event
                    # TODO: what if this is not true ?

                #--------------------------------
                # generate strings to display
                #--------------------------------

                string_temp_current = format(temp_current, '.0f') + u'\N{DEGREE SIGN}F'
                string_feels_like     = 'Feels like: ' + format(feels_like, '.0f') +  u'\N{DEGREE SIGN}F'
                string_humidity       = 'Humidity: ' + str(humidity) + '%'
                string_dewpt          = 'Dew Point: ' + format(dewpt, '.0f') +  u'\N{DEGREE SIGN}F'
                string_wind           = 'Wind: ' + format(wind, '.1f') + ' MPH ' + windcard
                #string_windcard = windcard
                string_report         = 'Now: ' + report.title()
                string_baro           = str(baro) + ' inHg'
                string_temp_max       = 'High: ' + format(temp_max, '>.0f') + u'\N{DEGREE SIGN}F'
                string_temp_min       = 'Low:  ' + format(temp_min, '>.0f') + u'\N{DEGREE SIGN}F'
                string_precip_percent = 'Precip: ' + str(format(daily_precip_percent, '.0f'))  + '%'
                if total_rain < 1000:
                    string_total_rain = 'Total: ' + str(format(total_rain, '.2f')) + ' in | Duration: ' + str(rain_time) + ' min'
                else:
                    string_total_rain = 'Total: Trace | Duration: ' + str(rain_time) + ' min'
                string_rain_time      = str(rain_time) + 'min'

                # Set error code to false to break out of this while loop
                error = False

            else:
                # Call function to display HTTP error
                display_error('HTTP')
                # TODO: shouldn't we sleep before trying again ?


        #------------------------------

        # at this point we've gotten Tempest WX current conditions
        # and the NWS alert information, so assemble the graphical
        # elements to display to the screen

        # TODO: this should be a generate_display_elements() routine

        # Open template file and initialize the drawing context
        #    with the template as background
        template = Image.open(os.path.join(picdir, 'template.png'))
        draw = ImageDraw.Draw(template)

        # Draw top left box
        #Logic for nighttime....DAYTIME
        nowcheck = datetime.now()
        if icon_code.startswith('possibly') or icon_code  == 'cloudy' or icon_code == 'foggy' or icon_code == 'windy' or icon_code.startswith('clear') or icon_code.startswith('partly'):
            icon_file = icon_code + '.png'
        elif nowcheck >= sunrise and nowcheck < sunset:
            icon_file = icon_code + '-day.png'
        else:
            icon_file = icon_code + '-night.png'
        icon_image = Image.open(os.path.join(icondir, icon_file))
        template.paste(icon_image, (40, 15))
        ## Place a black rectangle outline
        #draw.rectangle((25, 20, 225, 180), outline=black)
        draw.text((15, 183), string_report, font=font22, fill=black) #15, 190
        #Barometer trend logic block
        if trend == 'falling':
            baro_file = 'barodown.png'
        elif trend == 'steady':
            baro_file = 'barosteady.png'
        else: #trend == 'rising':
            baro_file = 'baroup.png'
        baro_image = Image.open(os.path.join(icondir, baro_file))
        template.paste(baro_image, (15, 213)) #15, 218
        draw.text((65, 223), string_baro, font=font22, fill=black) #65,228
        precip_file = 'precip.png'
        precip_image = Image.open(os.path.join(icondir, precip_file))
        template.paste(precip_image, (15, 255)) #15, 260
        draw.text((65, 263), string_precip_percent, font=font22, fill=black) #65, 268

        # Draw top right box
        draw.text((365, 35), string_temp_current, font=font160, fill=black) #375,35
        draw.text((360, 195), string_feels_like, font=font50, fill=black) #350,210
        difference = int(feels_like) - int(temp_current)
        if difference >= 5:
            feels_file = 'finghot.png'   #---- TODO: rename this (really dude?)
            feels_image = Image.open(os.path.join(icondir, feels_file))
            template.paste(feels_image, (720, 196))
        if difference <= -5:
            feels_file = 'fingcold.png'   #---- TODO: rename this (really dude?)
            feels_image = Image.open(os.path.join(icondir, feels_file))
            template.paste(feels_image, (720, 196))

        # Draw bottom left box
        draw.text((35, 330), string_temp_max, font=font50, fill=black) #35,325
        draw.line((170, 390, 265, 390), fill=black, width=4)
        draw.text((35, 395), string_temp_min, font=font50, fill=black) #35,390

        # Draw bottom middle box
        rh_file = 'rh.png'
        rh_image = Image.open(os.path.join(icondir, rh_file))
        template.paste(rh_image, (320, 320))
        draw.text((370, 330), string_humidity, font=font23, fill=black) #345, 340
        dp_file = 'dp.png'
        dp_image = Image.open(os.path.join(icondir, dp_file))
        template.paste(dp_image, (320, 373))
        draw.text((370, 383), string_dewpt, font=font23, fill=black)
        wind_file = 'wind.png'
        wind_image = Image.open(os.path.join(icondir, wind_file))
        template.paste(wind_image, (320, 425))
        draw.text((370, 435), string_wind, font=font23, fill=black) #345, 400
        #draw.text((535, 435), string_windcard, font=font23, fill=black)

        # Draw bottom right box
        #Begin Lightning mod
        if strikesraw >= 1:
            strike_file = 'strike.png'
            strike_image = Image.open(os.path.join(icondir, strike_file))
            template.paste(strike_image, (605, 305))
            draw.text((695, 330), 'Strikes', font=font22, fill=white)
            draw.line((690, 355, 765, 355), fill =white, width=3)
            draw.text((703, 360), strikes, font=font20, fill=white)
            draw.text((685, 400), 'Distance', font=font22, fill=white)
            draw.line((680, 425, 773, 425), fill =white, width=3)
            draw.text((683, 430), lightningdist, font=font20, fill=white)
        else:
            draw.text((627, 330), 'UPDATED', font=font35, fill=white)
            current_time = datetime.now().strftime('%H:%M')
            draw.text((627, 375), current_time, font = font60, fill=white)

        #Precipitaton mod
        if total_rain > 0 or total_rain == 1000:
            train_file = 'totalrain.png'
            train_image = Image.open(os.path.join(icondir, train_file))
            template.paste(train_image, (330, 15))
            draw.text((380, 22), string_total_rain, font=font23, fill=black)

        #Severe Weather Mod
        try:
             if string_event != None:
                alert_file = 'warning.png'
                alert_image = Image.open(os.path.join(icondir, alert_file))
                template.paste(alert_image, (335, 255))
                draw.text((385, 263), string_event, font=font23, fill=black)
        except NameError:
            print('No Severe Weather')

        # Save the image for display as PN
        screen_output_file = os.path.join(picdir, 'screen_output.png')
        template.save(screen_output_file) # TODO: this should go to /tmp

        # Close the template file
        template.close()

        # Write to screen
        if config['debug_screen'] == "True":
            print("  debug_screen is ..." , debug_screen)
            write_test_info(screen_output_file, 300)
        else:
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
