#-----------------------------------------------------------
# cron variant - this runs and exits after quieting the screen
#
# install in crontab ala:
#     2,7,12,17,22,27,32,37,42,47,52,57 * * * * cd /home/pi/Tempest-7.5-E-Paper-Display && python3 weather-cron.py >/tmp/program.out 2&>1
#     2-57/5 * * * * cd /home/pi/Tempest-7.5-E-Paper-Display && python3 weather-cron.py >/tmp/program.out 2&>1
#
# be sure to redirect stdout and stderr ala the example above
# or the program will likely not run ok via cron
#
#-----------------------------------------------------------
#
# note: for the 2-color display this needs to use the older
#       v4.0 version of the waveshare libs but the 3-color
#       still uses the original upstream (later) library
#
# also: I renamed the hot/cold icons to be less iffy :-)
#
# TODO: this does a full refresh.  Support incremental for gusts ?
#
# For icon codes, these are the possibilities....
#     icon codes with day/night and non-specific variants are:
#       rainy sleet snow thunderstorm
#
#     icon codes with day-night but no non-specific variant are:
#       clear partly-cloudy possibly-rainy possibly-sleet
#         possibly-snow possibly-thunderstorm
#
#     misc icons are:
#       barodown barosteady baroup
#       cloudy foggy verycold veryhot windy
#       dp precip rh strike totalrain warning wind
#
#     this one can replace 'windy' with a meme
#       windy-meme
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

#---------------------------------------------------------------

def convertToEpoch(dateTime):

    """
    convert a datetime.datetime.now() timestamp to epoch secs

    input: 2024-10-24 07:42:12.032869-07:00
    output: corresponding secs since the epoch
    """

    epoch = datetime.datetime(dateTime.year,dateTime.month,dateTime.day,dateTime.hour,dateTime.minute,dateTime.second).strftime('%s')
    return epoch

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

def write_to_screen(image, sleep_seconds):
    """
    Write a previously generated image to the screen
    and sleep for a specified period

    input: absolute path to the image, int(seconds)
    output: nothing
    """

    #TODO: should we epd.init 'and' epd.clear to prevent burn-in ?

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

def getWeewxConditions(conditions,units):

    '''
    get WeeWX weather conditions from the configured data_url

    input:  empty conditions and units hashes
    output: filled in hashes

    '''

    #TODO: need this in try/except block with failsafe values

    try:
        response = requests.get(config['data_url'])
        j = response.json()
    except:
        display_error('WEEWX_DATA')

    # tear it apart and stash the values, formatted appropriately
    conditions['baro']         = format(float(j['current']['barometer']['value']), '.02f')
    conditions['dewpt']        = format(float(j['current']['dewpoint']['value']) , '.0f' )
    conditions['feels_like']   = format(float(j['current']['appTemp']['value'])  , '.0f' )
    conditions['humidity']     = format(float(j['current']['humidity']['value']) , '.0f' )
    conditions['temp_current'] = format(float(j['current']['outTemp']['value'])  , '.0f' )
    conditions['temp_max']     = format(float(j['day']['high']['value'])         , '.0f' )
    conditions['temp_min']     = format(float(j['day']['low']['value'])          , '.0f' )
    conditions['total_rain']   = format(float(j['day']['rain']['value'])         , '.2f' )
    conditions['weekRain']     = format(float(j['week']['rain']['value'])        , '.2f' )
    conditions['wind']         = format(float(j['current']['windGust']['value']) , '.0f' )

    try:
        conditions['windcardinal'] = j['current']['windGustCardinal']['value']
    except:
        conditions['windcardinal'] = ""

    conditions['icon_code']    = "clear"  # we later supersede this

    conditions['sunrise']      = j['sunrise']
    conditions['sunset']       = j['sunset']
    conditions['periodOfDay']  = j['periodOfDay']
    conditions['updated']      = j['currentTime']

    conditions['description'] = "unknown"

    # trend is if +/- 1mb which is a little under 0.03 inHg
    barodiff = float(j['trend']['barometer']['value'])
    if barodiff >= 0.03:
        conditions['trend'] = "rising"
    elif barodiff <=-0.03:
        conditions['trend'] = "falling"
    else:
        conditions['trend'] = "steady"


    #TODO: this is US units, should handle users who chose metric or metricwx
    units['baro']         = "inHg"
    units['dewpt']        = u'\N{DEGREE SIGN}' + "F"
    units['feels_like']   = u'\N{DEGREE SIGN}' + "F"
    units['humidity']     = "%"
    units['temp_current'] = u'\N{DEGREE SIGN}' + "F"
    units['temp_max']     = u'\N{DEGREE SIGN}' + "F"
    units['temp_min']     = u'\N{DEGREE SIGN}' + "F"
    units['total_rain']   = "in"
    units['wind']         = "mph"
    units['weekRain']     = "in"
    units['precip_pct']   = "%"  # value comes from forecast

    # TODO: this is gross - convert to datetime object then strftime it to HH:MM
    #from datetime import datetime
    #conditions['updated'] = datetime.strptime(j['generation']['time'], "%Y-%m-%dT%H:%M:%S%z").strftime('%H:%M')

    return conditions, units

#-----------------------------------------------------------
# UNTESTED
# TODO: why does this sleep 30 and then try again seemingly infinitely ?
# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source +' ERROR', font=font35, fill=black)
    draw.text((100, 300), 'Retrying in 30 seconds', font=font22, fill=black)
    current_time = datetime.datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font = font35, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(tmpdir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen
    write_to_screen(error_image_file, 30)

#-----------------------------------------------------------

def get_nws_alerts(alerts_url):
    """
    Get any 'active' severe weather data from NWS

    input:  nothing
    output: string 'string_event'

    """

    if 'alerts' in config['debug']:
        print("trying to get weather alerts")
        print("   ") ; print(alerts_url)

    response = requests.get(alerts_url)
    nws = response.json()

    try:
        # check for the first alert
        alert       = nws['features'][int(0)]['properties']
        messageType = alert['messageType']
        expires     = alert['expires']
        currentTime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

        # if currentTime > alert['expires'] or messageType == "Cancel":
        #     try:
        #         # check for a second alert
        #         alert       = nws['features'][int(1)]['properties']
        #         messageType = alert['messageType']
        #         expires     = alert['expires']
        #         currentTime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        #         if currentTime > alert['expires'] or messageType == "Cancel":
        #             alert = None
        #     except IndexError:
        #         alert = None       # no second alert
        # else:
        #     print("alert = ", alert['event'])

    except IndexError:
        print("no alerts to process")
        alert    = None            # no first alert

    # if we still have one that wasn't canceled...
    if alert:
        event       = alert['event']
        urgency     = alert['urgency']
        severity    = alert['severity']

    # only care about some alert types - ignore misc. like "Hydrologic Outlook")
    if alert != None and (event.endswith('Warning') or event.endswith('Watch') or event.endswith('Statement') or event.endswith('Alert') or event.endswith('Advisory')):
        string_event = event
    else:
        string_event = None

    return string_event

#-----------------------------------------------------------

def get_nws_forecast(forecast_url,forecast):

    """
    Get Forecast from NWS

    input:  empty forecast hash
    output: forecast
    """

    if 'forecasts' in config['debug']:
        print("trying to get weather forecasts from", forecast_url)
    response = requests.get(forecast_url)
    nws = response.json()
    try:
        # note this gets the first forecast only, there might be multiple ones in the NWS payload
        currentForecast    = nws['properties']['periods'][0]
    except IndexError:
        currentForecast    = None

    if currentForecast:
        #TODO: handle response of 'null' without quotes
        forecast['precip_pct'] = currentForecast['probabilityOfPrecipitation']['value']
        forecast['icon_code']  = str.lower(currentForecast['shortForecast'])
        forecast['shortForecast']  = currentForecast['shortForecast']

    return forecast

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

# initialize some hashes used below
conditions = {}
config     = {}
forecast   = {}
units      = {}

# read the config file
config = read_config_file('config.json')
if 'config' in config['debug']:
    print(config)

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

#------------ main -----------

periodOfDay = None   # initialize

now = datetime.datetime.now()

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

        now = datetime.datetime.now()

        ###############
        # debug - force time to night using some time and date object lunacy
        #    ref: https://stackoverflow.com/questions/71323493/how-to-convert-time-object-to-datetime-object-in-python/71323494
        # tmpnow   ="2024-10-29 02:11:23"
        # timenow = time.strptime(tmpnow, '%Y-%m-%d %H:%M:%S')
        # now     = datetime.datetime(*timenow[:5])
        ###############

        #---------------------------------------------------------------
        # get current conditions
        #---------------------------------------------------------------

        (conditions,units) = getWeewxConditions(conditions,units)

        if 'conditions' in config['debug']:
            print("conditions = ",  conditions)
            print("units      = ",  units)

        #---------------------------------------------------------------
        # optionally show current time, periodOfDay, sunrise, sunset
        #---------------------------------------------------------------

        if 'datetime' in config['debug']:
            print("current:", now, " is in ", conditions['periodOfDay'])
            print("sunrise:", conditions['sunrise'])
            print("sunset :", conditions['sunset'])

        #---------------------------------------------------------------
        # get forecast
        #---------------------------------------------------------------

        if 'forecast' in config['debug']:
            print("getting nws forecast")

        forecast_url = config['forecast_url']

        #config['forecast_url'] = "https://api.weather.gov/gridpoints/GLD/116,80/forecast" # DEBUG ODD LOCATION

        # TODO: this should be in a try/except
        try:
            forecast = get_nws_forecast(config['forecast_url'],forecast)
        except:
            forecast = None

        if 'forecast' in config['debug']:
            print(forecast)
            print("forecast  : ", forecast)

        #---------------------------------------------------------------
        # get alerts
        #---------------------------------------------------------------

        # TODO: what if they want alerts from other sources ???
        alerts_url = config['alerts_url']

        ####alerts_url = "https://api.weather.gov/alerts/active?zone=CAZ072" # Tahoe for test use only

        try:
            event = get_nws_alerts(alerts_url)
            conditions['event'] = event
            if "alerts" in config['debug']:
                print("alerts = ", event)
                print(event)
        except:
            print("fail getting alerts")
            conditions['event'] = None

        #---------------------------------------------------------------
        # generate some strings with units and/or rounding as applicable
        #---------------------------------------------------------------

        #TODO: the try/except for no forecast available needs work below...

        # the units are defined and values formatted above in getWeewxConditions

        string_temp_max = 'High: ' + str(conditions['temp_max']) + units['temp_max']
        string_temp_min = 'Low:  ' + str(conditions['temp_min']) + units['temp_min']

        string_baro = str(conditions['baro']) +  ' ' + units['baro']

        try:
            string_precip_percent = 'Precip: ' + str(forecast['precip_pct'])  + " " + units['precip_pct']
        except:
            string_precip_percent = 'Precip: unavail'

        string_feels_like = 'Feels like: ' + str(conditions['feels_like']) + units['feels_like']
        string_temp_current = str(conditions['temp_current']) + units['temp_current']
        string_humidity = 'Humidity: ' + str(conditions['humidity']) + " " + units['humidity']
        string_dewpt = 'Dew Point: ' + str(conditions['dewpt']) + units['dewpt']
        string_wind = 'Wind: ' + str(conditions['wind']) + " " + units['wind'] + " " + conditions['windcardinal']

        # "Chance Rain Showers" is 3 char too long to fit
        try:
            string_description = forecast['shortForecast']
        except:
            string_description = None

        if len(forecast['shortForecast']) < 18:
            string_description = 'Now: ' + forecast['shortForecast']
        else:
            # handle things like "Partly Sunny then Chance Rain Showers"
            string_description = forecast['shortForecast'].split('then',1)[0]
            # and like "Showers And Thunderstorms Likely"
            string_description = string_description.split('And',1)[0]

        if "shortForecast" in config['debug']:
            print("shortForecast: ", forecast['shortForecast'])

        if conditions['event']:
            string_event = conditions['event']
        else:
            string_event = ""

        string_total_rain = 'Total: ' + \
            str(conditions['total_rain']) + " " + units['total_rain'] + " | Week: " \
            + str(conditions['weekRain']) + " " + units['weekRain']\

        #------------------------------------------------------------------------
        #---------------- start assembling the image ----------------------------
        #------------------------------------------------------------------------

        # the base image
        template = Image.open(os.path.join(picdir, 'template.png'))
        draw = ImageDraw.Draw(template)

        #------------------------------------------------------------------------
        #---------------- overlay data onto the image ---------------------------
        #----------------           start             ---------------------------
        #------------------------------------------------------------------------

        #--------  top left box -------

        #TODO: need all NWS variants of what shortForecast might be

        if forecast:
            icon_code = forecast['icon_code']
        else:
            icon_code = None

        if 'rain' in icon_code:
            icon_code = 'rainy'
        elif 'cloudy' in icon_code:
            icon_code = 'cloudy'
        elif 'sleet' in icon_code:
            icon_code = 'sleet'
        elif 'snow' in icon_code:
            icon_code = 'snow'
        elif 'thunder' in icon_code:
            icon_code = 'thunderstorm'
        elif 'clear' in icon_code:
            icon_code = 'clear'
        elif 'fog' in icon_code:
            icon_code = 'foggy'
        elif 'sunny' in icon_code:
            icon_code = 'clear'

        #TODO: these are WF variants - need the syntax for NWS forecast variants
        # some icons have no day/night variants
        if icon_code.startswith('possibly') or icon_code  == 'cloudy' or icon_code == 'foggy' or icon_code == 'windy' or icon_code.startswith('partly'):
            icon_file = icon_code + '.png'
        elif conditions['periodOfDay'] != None:
            if conditions['periodOfDay'] == "day":
                icon_file = icon_code + '-day.png'
            else:
                icon_file = icon_code + '-night.png'
        else:
            icon_file = icon_code + '.png'

        try:
            icon_image = Image.open(os.path.join(icondir, icon_file))
        except:
            print("ERROR - cannot open", icon_file)
            icon_image = Image.open(os.path.join(icondir, 'warning.png'))

        template.paste(icon_image, (40, 15))
        draw.text((15, 183), string_description, font=font22, fill=black)

        if conditions['trend'] == "falling":
            baro_file = 'barodown.png'
        elif conditions['trend'] == "steady":
            baro_file = 'barosteady.png'
        elif conditions['trend'] == "rising":
            baro_file = 'baroup.png'

        baro_image = Image.open(os.path.join(icondir, baro_file))
        template.paste(baro_image, (15, 213))
        draw.text((65, 223),  string_baro                     , font=font22,  fill=black)  # baro

        precip_file = 'precip.png'
        precip_image = Image.open(os.path.join(icondir, precip_file))
        template.paste(precip_image, (15, 255))
        draw.text((65, 263),  string_precip_percent           , font=font22,  fill=black)  # precip_pct

        #--------  bottom left box -------
        draw.text((35, 330),  string_temp_max                 , font=font50,  fill=black)  # temp_max
        draw.text((35, 395),  string_temp_min                 , font=font50,  fill=black)  # temp_min

        #--------  top right box -------
        draw.text((380, 22),  string_total_rain               , font=font23,  fill=black)  # total_rain
        draw.text((365, 35),  string_temp_current             , font=font160, fill=black)  # temp_current
        draw.text((360, 195), string_feels_like               , font=font50,  fill=black)  # feels_like

        # possible weather event text
        try:
            if conditions['event'] != None:
                alert_image = Image.open(os.path.join(icondir, "warning.png"))
                template.paste(alert_image, (335, 255))
                draw.text((385, 263), str(conditions['event']) , font=font23, fill=black)
        except NameError:
            print('No Severe Weather')

        # TODO: the +/- range likely needs tweaking for imperial units

        # change the feels_like icon if it is hot or cold
        difference = int(conditions['feels_like']) - int(conditions['temp_current'])
        if difference >= 5:
            feels_file = 'veryhot.png'
            feels_image = Image.open(os.path.join(icondir, feels_file))
            template.paste(feels_image, (720, 196))
        if difference <= -5:
            feels_file = 'verycold.png'
            feels_image = Image.open(os.path.join(icondir, feels_file))
            template.paste(feels_image, (720, 196))

        #--------  bottom middle box -------
        draw.text((370, 330), string_humidity                 , font=font23,  fill=black)  # humidity
        draw.text((370, 383), string_dewpt                    , font=font23,  fill=black)  # dewpt
        draw.text((370, 435), string_wind                     , font=font23,  fill=black)  # wind
        draw.text((385, 263), ""                              , font=font23,  fill=black)  # event

        # relative humidity
        rh_file = 'rh.png'
        rh_image = Image.open(os.path.join(icondir, rh_file))
        template.paste(rh_image, (320, 320))

        # dew point
        dp_file = 'dp.png'
        dp_image = Image.open(os.path.join(icondir, dp_file))
        template.paste(dp_image, (320, 373))

        # wind
        wind_file = 'wind.png'
        wind_image = Image.open(os.path.join(icondir, wind_file))
        template.paste(wind_image, (320, 425))

        # total_rain only if we have rain
        # TODO: or if it equals 1000 (huh?)
        train_image = Image.open(os.path.join(icondir, "totalrain.png"))
        template.paste(train_image, (330, 15))
        draw.text((380, 22), string_total_rain, font=font23, fill=black)

        #--------  bottom right box -------

        # HH:MM last updated
        draw.text((627, 330), 'UPDATED', font=font35, fill=white)
        draw.text((627, 375), conditions['updated'], font = font60, fill=white)  # HH:MM

        #------------------------------------------------------------------------
        #---------------- overlay data onto the image ---------------------------
        #----------------          done               ---------------------------
        #------------------------------------------------------------------------

        # save the aggregate image to a temporary file
        screen_output_file = os.path.join(tmpdir, 'screen_output.png')
        template.save(screen_output_file)

        # Close the template file
        template.close()

        # write generated output file to screen
        write_to_screen(screen_output_file, 300)

        # exit gracefully we hope so we can call this from cron periodically
        epd.sleep()
        sys.exit(0)

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


sys.exit(0)

#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------

"""
----------- BEGIN OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- BEGIN OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- BEGIN OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- BEGIN OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------

# Tampa is FLZ151
# Tahoe is CAZ072

----------- END OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- END OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- END OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------
----------- END OF STASHED DIFFS ETC TO (RE)INCLUDE ABOVE ------------

Traceback (most recent call last):
  File "/home/pi/Tempest-7.5-E-Paper-Display/weather.py", line 406, in <module>
    forecast = get_nws_forecast(config['forecast_url'],forecast)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/pi/Tempest-7.5-E-Paper-Display/weather.py", line 278, in get_nws_forecast
    currentForecast    = nws['properties']['periods'][0]
                         ~~~^^^^^^^^^^^^^^
KeyError: 'properties'
"""
