from typing import Any
import asyncio
import httpx
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()
# Tải thử từ thư mục gốc của repo
load_dotenv("../../.env")

# Initialize FastMCP server
port = int(os.getenv("PORT", 8085))
mcp = FastMCP("weather", host="0.0.0.0", port=port)

# Constants
WEATHERAPI_BASE = "https://api.weatherapi.com/v1"
USER_AGENT = "weather-app/1.0"

# Get API key from environment variable
API_KEY = os.getenv("WEATHERAPI_KEY")

async def make_weather_request(endpoint: str, params: dict[str, str]) -> dict[str, Any] | None:
    """Make a request to the WeatherAPI with proper error handling."""
    # Check if API key is set
    if not API_KEY:
        print("ERROR: WeatherAPI key not set. Please set WEATHERAPI_KEY environment variable.")
        return None
        
    headers = {
        "User-Agent": USER_AGENT,
    }
    # Add API key to parameters
    params["key"] = API_KEY
    
    url = f"{WEATHERAPI_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error {e.response.status_code}: {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get current weather conditions for a city.

    Args:
        city: City name (e.g., "Hanoi", "Haiphong", "Danang", "Brisbane", "Sydney")
    """
    params = {
        "q": city,
        "aqi": "no"
    }
    
    data = await make_weather_request("current.json", params)
    import json

    if not data:
        if not API_KEY:
            # Fallback sang Mock Data nếu người dùng chưa có API Key
            import logging
            logging.warning(f"⚠️ Không có WEATHERAPI_KEY. Trả về dữ liệu giả lập (mock data) cho {city}")
            return json.dumps({
                "city": city.title(),
                "country": "Vietnam (Mock)",
                "temperature": 28.5,
                "condition": "Partly cloudy (Mock)",
                "humidity": 75,
                "wind": "10.0 km/h NE",
                "last_updated": "2026-07-02 10:00"
            }, ensure_ascii=False)
        return json.dumps({"error": f"Unable to fetch current weather data for {city}. Please check the city name and API key configuration."})

    current = data["current"]
    location = data["location"]
    
    return json.dumps({
        "city": location["name"],
        "country": location["country"],
        "temperature": current["temp_c"],
        "condition": current["condition"]["text"],
        "humidity": current["humidity"],
        "wind": f"{current['wind_kph']} km/h {current['wind_dir']}",
        "last_updated": current["last_updated"]
    }, ensure_ascii=False)

@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Args:
        city: City name (e.g., "Hanoi", "Haiphong", "Danang", "Brisbane", "Sydney", "Melbourne")
        days: Number of days to forecast (1-3)
    """
    if days < 1 or days > 3:
        return f"❌ Lỗi: Tham số 'days' phải từ 1 đến 3. Bạn đã yêu cầu {days} ngày."
        
    params = {
        "q": city,
        "days": str(days),
        "aqi": "no",
        "alerts": "no"
    }
    
    data = await make_weather_request("forecast.json", params)

    if not data:
        if not API_KEY:
            # Fallback sang Mock Data nếu người dùng chưa có API Key
            logging.warning(f"⚠️ Không có WEATHERAPI_KEY. Trả về dữ liệu dự báo giả lập (mock data) cho {city}")
            return f"""Dự báo thời tiết giả lập (Mock) cho {city.title()}:
- Hôm nay: 28°C - 32°C, Có mây rải rác.
- Ngày mai: 27°C - 31°C, Khả năng có mưa rào.
(Vui lòng cung cấp WEATHERAPI_KEY để xem dữ liệu thật)"""
        return f"Unable to fetch forecast data for {city}. Please check the city name and API key configuration."

    location = data["location"]
    forecast_days = data["forecast"]["forecastday"]
    
    forecasts = []
    forecasts.append(f"Weather Forecast for {location['name']}, {location['region']}, {location['country']}:")
    
    for day in forecast_days:
        day_data = day["day"]
        date = day["date"]
        
        forecast = f"""
{date}:
High: {day_data['maxtemp_c']}°C ({day_data['maxtemp_f']}°F)
Low: {day_data['mintemp_c']}°C ({day_data['mintemp_f']}°F)
Condition: {day_data['condition']['text']}
Chance of Rain: {day_data['daily_chance_of_rain']}%
Max Wind: {day_data['maxwind_kph']} km/h
UV Index: {day_data['uv']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for deployment verification."""
    from datetime import datetime
    import logging
    import json
    logging.info("Health check requested")
    
    return json.dumps({
        "status": "ok",
        "server": "weather-mcp",
        "timestamp": datetime.now().isoformat(),
        "weather_api_configured": bool(API_KEY)
    })

import logging
logging.basicConfig(level=logging.INFO)
logging.info("✅ MCP server initialized with Streamable HTTP transport")
logging.info("🔧 Available tools: get_current_weather, get_forecast, health_check")

if __name__ == "__main__":
    import sys
    
    is_cloud_run = bool(os.getenv("PORT"))
    is_standalone = len(sys.argv) == 1 and sys.stdin.isatty()
    
    if is_cloud_run or is_standalone:
        print(f"🚀 Starting MCP server on http://0.0.0.0:{port}/mcp")
        mcp.run(transport="streamable-http")
    else:
        print("Starting FastMCP server in stdio mode for local client", file=sys.stderr)
        mcp.run()