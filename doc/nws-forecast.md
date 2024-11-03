
## How to determine your NWS forecast zone 

Ref: https://www.weather.gov/documentation/services-web-api

This example assumes your lat = 47.00 and lon = -122.00....


1. Look up your forecast zone URL

```
curl https://api.weather.gov/points/47.00,-122.00 

which returns content including:
 "forecast": "https://api.weather.gov/gridpoints/SEW/129,38/forecast"
 "forecastHourly": "https://api.weather.gov/gridpoints/SEW/129,38/forecast/hourly"
 "forecastZone": "https://api.weather.gov/zones/forecast/WAZ569"
```

2. Query the forecastZone URL for your forecast.

```
curl "https://api.weather.gov/gridpoints/SEW/129,38/forecast"

which returns a list of properties['periods'] ala:

        "periods": [
            {
                "number": 1,
                "name": "Today",
                "startTime": "2024-10-25T10:00:00-07:00",
                "endTime": "2024-10-25T18:00:00-07:00",
                "isDaytime": true,
                "temperature": 63,
                "temperatureUnit": "F",
                "temperatureTrend": "",
                "probabilityOfPrecipitation": {
                    "unitCode": "wmoUnit:percent",
                    "value": null
                },
                "windSpeed": "5 mph",
                "windDirection": "SE",
                "icon": "https://api.weather.gov/icons/land/day/bkn?size=medium",
                "shortForecast": "Partly Sunny",
                "detailedForecast": "Partly sunny. High near 63, with temperatures falling to around 59 in the afternoon. Southeast wind around 5 mph. New rainfall amounts less than a tenth of an inch possible."
            },

The current forecast is the first element in the list,  so....

    forecast                         = properties['periods'][0]
    forecast_temp                    = forecast['temperature']
    forecast_precip_pct              = forecast['probabilityOfPrecipitation']['value']
    forecast_wind                    = forecast['windSpeed']
    forecast_wind_cardinal_direction = forecast['windDirection']
    forecast_string                  = forecast['shortForecast']

careful on some values, they might read "10 to 14 mph" or even null as the example above indicates

```
