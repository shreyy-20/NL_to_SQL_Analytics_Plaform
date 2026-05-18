import httpx
import logging

logger = logging.getLogger(__name__)

class OpenMeteoService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    # Indian cities coordinates
    CITY_COORDINATES = {
        "bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
        "cuttack": {"lat": 20.4625, "lon": 85.8833},
        "puri": {"lat": 19.8135, "lon": 85.8312},
        "balasore": {"lat": 21.4927, "lon": 86.9335},
        "sambalpur": {"lat": 21.4667, "lon": 83.9667},
        "raurkeela": {"lat": 22.2257, "lon": 84.7890},
        "berhampur": {"lat": 19.3167, "lon": 84.7833},
    }
    
    async def get_weather_forecast(self, location: str, days: int = 7):
        """Get weather forecast for an Indian city"""
        location_key = location.lower().strip()
        
        if location_key not in self.CITY_COORDINATES:
            return None
        
        coords = self.CITY_COORDINATES[location_key]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "daily": "temperature_2m_max,temperature_2m_min,rain_sum,weathercode",
                    "timezone": "Asia/Kolkata",
                    "forecast_days": days
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_weather_response(data)
            return None
    
    def _format_weather_response(self, data):
        """Format Open-Meteo response for KrishiQuery"""
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        rain = daily.get("rain_sum", [])
        weather_codes = daily.get("weathercode", [])
        
        # Weather code mapping
        weather_desc = {
            0: "Clear sky ☀️",
            1: "Mainly clear 🌤️",
            2: "Partly cloudy ⛅",
            3: "Overcast ☁️",
            45: "Foggy 🌫️",
            51: "Light drizzle 🌦️",
            61: "Rain 🌧️",
            63: "Moderate rain 🌧️",
            65: "Heavy rain ☔",
            71: "Light snow ❄️",
            80: "Rain showers 🌦️",
            95: "Thunderstorm ⛈️"
        }
        
        forecast = []
        for i in range(min(len(dates), 7)):
            forecast.append({
                "date": dates[i],
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "rainfall": rain[i] if i < len(rain) else 0,
                "condition": weather_desc.get(weather_codes[i] if i < len(weather_codes) else 0, "Unknown")
            })
        
        return forecast