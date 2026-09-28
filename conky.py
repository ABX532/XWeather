import json
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import openmeteo_requests

BASE = Path(__file__).resolve().parent
CACHE = BASE / 'location.json'
ICON_DIR = BASE / 'icons'
ICON_DIR.mkdir(parents=True, exist_ok=True)
LOGO_PNG = BASE / 'xweather_logo.png'

api = openmeteo_requests.Client()
ICON_URL = 'https://openweathermap.org/img/wn/{code}@2x.png'


def get_location():
    try:
        req = Request('https://ipwho.is/', headers={'User-Agent': 'XWeather/1.0'})
        with urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())

        if not data.get('success', True):
            raise RuntimeError('IP geolocation failed')

        location = {
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'city': data.get('city') or 'Unknown',
            'region': data.get('region') or '',
            'country': data.get('country') or '',
        }
        CACHE.write_text(json.dumps(location), encoding='utf-8')
        return location
    except Exception:
        if CACHE.exists():
            return json.loads(CACHE.read_text(encoding='utf-8'))
        raise RuntimeError('Unable to determine location')


def get_weather(lat, lon):
    air_params = {'latitude': lat, 'longitude': lon, 'current': ['us_aqi'], 'timezone': 'auto'}
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': ['temperature_2m', 'relative_humidity_2m', 'weather_code', 'wind_speed_10m', 'wind_direction_10m', 'is_day'],
        'hourly': ['precipitation_probability'],
        'daily': ['sunrise', 'sunset', 'temperature_2m_max', 'temperature_2m_min', 'weather_code'],
        'forecast_days': 7,
    }

    last_error = None
    for attempt in range(3):
        try:
            air = api.weather_api('https://air-quality-api.open-meteo.com/v1/air-quality', params=air_params)[0]
            weather = api.weather_api('https://api.open-meteo.com/v1/forecast', params=params)[0]
            return air, weather
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2)
    raise last_error


def condition(code):
    return {
        0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Rime fog', 51: 'Light drizzle', 53: 'Drizzle', 55: 'Heavy drizzle',
        56: 'Freezing drizzle', 57: 'Freezing drizzle', 61: 'Light rain', 63: 'Rain',
        65: 'Heavy rain', 66: 'Freezing rain', 67: 'Freezing rain', 71: 'Light snow',
        73: 'Snow', 75: 'Heavy snow', 77: 'Snow grains', 80: 'Rain showers',
        81: 'Rain showers', 82: 'Heavy showers', 85: 'Snow showers', 86: 'Heavy snow showers',
        95: 'Thunderstorm', 96: 'Thunderstorm', 99: 'Thunderstorm',
    }.get(code, 'Unknown')


def openweather_icon(code, night=False):
    if code == 0: icon = '01'
    elif code == 1: icon = '02'
    elif code == 2: icon = '03'
    elif code == 3: icon = '04'
    elif code in (45, 48): icon = '50'
    elif 51 <= code <= 57 or 80 <= code <= 82: icon = '09'
    elif 61 <= code <= 67: icon = '10'
    elif 71 <= code <= 77 or 85 <= code <= 86: icon = '13'
    elif 95 <= code <= 99: icon = '11'
    else: icon = '03'
    return icon + ('n' if night else 'd')


def ensure_icon(icon_id):
    path = ICON_DIR / f'{icon_id}.png'
    if path.exists() and path.stat().st_size > 100:
        return path
    try:
        req = Request(ICON_URL.format(code=icon_id), headers={'User-Agent': 'XWeather/1.0'})
        with urlopen(req, timeout=8) as r:
            path.write_bytes(r.read())
        return path
    except Exception:
        return None


def image(path, x, y, size):
    if not path:
        return ''
    return f'${{image {path} -p {x},{y} -s {size}x{size}}}'


def day_name(offset, now):
    if offset == 0: return 'TODAY'
    if offset == 1: return 'TOMORROW'
    return ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'][(now.weekday() + offset) % 7]


def main():
    loc = get_location()
    air, response = get_weather(loc['latitude'], loc['longitude'])
    current, hourly, daily = response.Current(), response.Hourly(), response.Daily()

    temp = round(current.Variables(0).Value())
    humidity = round(current.Variables(1).Value())
    code = int(current.Variables(2).Value())
    wind = round(current.Variables(3).Value())
    wind_dir = round(current.Variables(4).Value())
    is_day = bool(round(current.Variables(5).Value()))
    aqi = round(air.Current().Variables(0).Value())

    now = datetime.fromtimestamp(current.Time())
    rain = round(hourly.Variables(0).ValuesAsNumpy()[now.hour])
    sunrise = datetime.fromtimestamp(daily.Variables(0).ValuesInt64AsNumpy()[0]).strftime('%H:%M')
    sunset = datetime.fromtimestamp(daily.Variables(1).ValuesInt64AsNumpy()[0]).strftime('%H:%M')
    max_t = [round(x) for x in daily.Variables(2).ValuesAsNumpy()]
    min_t = [round(x) for x in daily.Variables(3).ValuesAsNumpy()]
    daily_codes = [int(x) for x in daily.Variables(4).ValuesAsNumpy()]

    sectors = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    wind_text = sectors[round(wind_dir / 22.5) % 16]
    if aqi <= 50: aqi_color, aqi_label = '#78D6A3', 'GOOD'
    elif aqi <= 100: aqi_color, aqi_label = '#F2C66D', 'MODERATE'
    else: aqi_color, aqi_label = '#FF8A8A', 'POOR'

    place = f"{loc['city']}, {loc['country']}" if loc['country'] else loc['city']
    main_icon = ensure_icon(openweather_icon(code, night=not is_day))
    forecast_icons = [ensure_icon(openweather_icon(c)) for c in daily_codes]

    # This is intentionally the original v6 layout. Only location/path handling was changed.
    out = []
    out.append(image(LOGO_PNG, 30, 33, 34))
    out.append('${goto 72}${voffset 2}${font Rubik Bold:size=12}${color #FFFFFF}XWeather${color}${font}')
    out.append('${goto 72}${voffset 0}${font Rubik:size=8}${color #8999C8}' + place.upper() + '${color}${font}')
    out.append('${goto 31}${voffset 18}${font Rubik:size=36}${color #F7F8FF}' + str(temp) + '°${color}${font}')
    out.append('${goto 33}${font Rubik:size=9}${color #AAB5D8}' + condition(code) + '${color}${font}')
    out.append(image(main_icon, 226, 75, 82))
    out.append('${goto 31}${font Rubik Bold:size=8}${color #7183FF}CURRENT${color}${font}')
    out.append('${goto 31}${font Rubik:size=8}${color #8999C8}TEMP${color} ${goto 93}${color #F4F5FA}' + f'{temp}°C' + '${color}${font}' + '${goto 173}${color #8999C8}HUMIDITY${color} ${goto 246}${color #F4F5FA}' + f'{humidity}%' + '${color}${font}')
    out.append('${goto 31}${font Rubik:size=8}${color #8999C8}WIND${color} ${goto 93}${color #F4F5FA}' + f'{wind} km/h {wind_text}' + '${color}${font}' + '${goto 173}${color #8999C8}RAIN${color} ${goto 246}${color #F4F5FA}' + f'{rain}%' + '${color}${font}')
    out.append('${goto 31}${font Rubik Bold:size=8}${color #7183FF}SUN${color}${font}')
    out.append('${goto 31}${font Rubik:size=8}${color #8999C8}SUNRISE${color} ${goto 93}${color #F4F5FA}' + sunrise + '${color}${font}' + '${goto 173}${color #8999C8}SUNSET${color} ${goto 246}${color #F4F5FA}' + sunset + '${color}${font}')
    out.append('${goto 31}${font Rubik Bold:size=8}${color #7183FF}AIR QUALITY${color}${font}')
    out.append('${goto 31}${font Rubik Bold:size=15}${color ' + aqi_color + '}' + str(aqi) + '${color}${font} ${font Rubik:size=8}${color #AAB5D8}' + aqi_label + '${color}${font}')
    out.append('${goto 31}${font Rubik Bold:size=8}${color #7183FF}7-DAY FORECAST${color}${font}')

    for i in range(7):
        y = 315 + i * 31.7
        out.append(image(forecast_icons[i], 111, y, 25))
        out.append('${goto 31}${font Rubik:size=8}${color #AAB5D8}' + f'{day_name(i, now):<9}' + '${goto 145}${color #F4F5FA}' + f'{max_t[i]:>2}°' + '${color #687492}' + f' / {min_t[i]:>2}°' + '${goto 215}${color #9EA9C8}' + condition(daily_codes[i]) + '${color}${font}')

    out.append('${goto 31}${font Rubik:size=7}${color #65708E}UPDATED ' + now.strftime('%H:%M') + '  •  OPEN-METEO${color}${font}')
    print('\n'.join(out))


try:
    main()
except Exception:
    print('${goto 31}${font Rubik Bold:size=12}${color #FFFFFF}XWeather${color}${font}')
    print('${goto 31}${font Rubik:size=9}${color #FF9090}Weather unavailable${color}${font}')
    print('${goto 31}${font Rubik:size=8}${color #8999B8}Retrying automatically...${color}${font}')
