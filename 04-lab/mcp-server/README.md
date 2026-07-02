# Weather MCP Server (Lab 04)

MCP Server cung cấp dữ liệu thời tiết thực tế từ WeatherAPI.com, chạy qua giao thức **Streamable HTTP**.

## 1. Setup & Environment

Bạn cần đăng ký một tài khoản miễn phí tại [WeatherAPI](https://www.weatherapi.com/) để lấy API key.

Sao chép file `.env` hoặc thiết lập biến môi trường:
```bash
export WEATHERAPI_KEY="your_weatherapi_key_here"
# export PORT=8085 (Tuỳ chọn, mặc định là 8085)
```

## 2. Cách chạy (Run Command)

Di chuyển vào thư mục `mcp-server` và khởi động server bằng `uv`:
```bash
cd mcp-server
uv sync
uv run python weather.py
```
Server sẽ lắng nghe tại: `http://localhost:8085/mcp` (dành cho Streamable HTTP transport).

## 3. Các Tools cung cấp (Exposed Tools)

- `get_current_weather(city: str)`: Lấy thông vị thời tiết hiện tại cho một thành phố.
- `get_forecast(city: str, days: int)`: Lấy dự báo thời tiết từ 1 đến 3 ngày.
- `health_check()`: Kiểm tra trạng thái hoạt động của MCP server.

## 4. Dữ liệu mẫu (Example Responses)

**`get_current_weather("Hanoi")`**:
```json
{
  "city": "Hanoi",
  "country": "Vietnam",
  "temperature": 29.0,
  "condition": "Light rain",
  "humidity": 82,
  "wind": "12.0 km/h SE",
  "last_updated": "2023-10-25 10:00"
}
```

**`get_forecast("Hanoi", days=1)`**:
```text
Weather Forecast for Hanoi, Hanoi, Vietnam:
2023-10-26:
High: 31.0°C (87.8°F)
Low: 24.0°C (75.2°F)
Condition: Patchy rain possible
Chance of Rain: 70%
Max Wind: 15.0 km/h
UV Index: 6.0
```

**`health_check()`**:
```json
{
  "status": "ok",
  "server": "weather-mcp",
  "timestamp": "2026-07-02T10:00:00.000000",
  "weather_api_configured": true
}
```
