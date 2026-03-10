import requests
from datetime import datetime

class WeatherException(Exception):
    pass

class Weather:
    def __init__(self, config):
        self.api_key = config.get('API_KEY')
        self.api_url = config.get('API_URL')
        self.location = None

    def set_location(self, location):
        self.location = location

    def get_forecast_data(self):
        if not self.location:
            raise WeatherException("No location set")

        # Get current weather (more detailed)
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.location}&appid={self.api_key}&units=metric"
        # Get 5-day forecast
        forecast_url = f"{self.api_url}?q={self.location}&appid={self.api_key}&units=metric"

        try:
            current_resp = requests.get(current_url, timeout=10)
            forecast_resp = requests.get(forecast_url, timeout=10)

            if current_resp.status_code != 200:
                raise WeatherException("City not found")

            current = current_resp.json()
            forecast = forecast_resp.json()

            # Sunrise/sunset
            sunrise = datetime.fromtimestamp(current['sys']['sunrise']).strftime('%I:%M %p')
            sunset = datetime.fromtimestamp(current['sys']['sunset']).strftime('%I:%M %p')

            # Process 5-day forecast (one per day)
            daily = {}
            for item in forecast['list']:
                date = datetime.fromtimestamp(item['dt']).strftime('%A, %b %d')
                if date not in daily:
                    daily[date] = {
                        'date': date,
                        'temp_max': item['main']['temp_max'],
                        'temp_min': item['main']['temp_min'],
                        'description': item['weather'][0]['description'].title(),
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity'],
                        'wind': item['wind']['speed'],
                    }
                else:
                    daily[date]['temp_max'] = max(daily[date]['temp_max'], item['main']['temp_max'])
                    daily[date]['temp_min'] = min(daily[date]['temp_min'], item['main']['temp_min'])

            return {
                'city': current['name'],
                'country': current['sys']['country'],
                'temp': round(current['main']['temp']),
                'feels_like': round(current['main']['feels_like']),
                'temp_min': round(current['main']['temp_min']),
                'temp_max': round(current['main']['temp_max']),
                'humidity': current['main']['humidity'],
                'pressure': current['main']['pressure'],
                'wind_speed': current['wind']['speed'],
                'wind_deg': current['wind'].get('deg', 0),
                'clouds': current['clouds']['all'],
                'visibility': current.get('visibility', 0) // 1000,
                'description': current['weather'][0]['description'].title(),
                'icon': current['weather'][0]['icon'],
                'sunrise': sunrise,
                'sunset': sunset,
                'forecast': list(daily.values())[:5],
            }

        except requests.exceptions.RequestException:
            raise WeatherException("Network error")
