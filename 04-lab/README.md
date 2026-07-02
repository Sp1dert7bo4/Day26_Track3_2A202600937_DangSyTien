# Lab 04 — Weather Agent with Remote MCP Server

A weather agent built with Google ADK that connects to an MCP server via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐   Streamable HTTP    ┌─────────────────┐      REST       ┌─────────────────┐
│   ADK Agent     │ ──────────────────── │   MCP Server    │ ─────────────── │  WeatherAPI.com │
│  (mcp-client)   │   localhost:8085/mcp │  (mcp-server)   │                 │                 │
└─────────────────┘                      └─────────────────┘                 └─────────────────┘
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Get current weather conditions for a city |
| `get_forecast(city, days)` | Get weather forecast (1–3 days) |
| `health_check()` | Verify server is running |

## ADK làm gì trong Lab này?

ADK (Agent Development Kit) đóng vai trò **MCP Client** 
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. KẾT NỐI tới MCP Server qua Streamable HTTP                  │
│     StreamableHTTPConnectionParams(url="localhost:8085/mcp")    │
│                                                                 │
│  2. KHÁM PHÁ tools tự động (list_tools)                         │
│     McpToolset → tự hỏi server "anh có tool gì?"                │
│     → nhận về: get_current_weather, get_forecast, health_check  │
│                                                                 │
│  3. TRUYỀN tools cho LLM (Gemini)                               │
│     Agent(model="gemini-2.5-flash", tools=[weather_tools])      │
│     → Gemini biết nó có thể gọi 3 tools trên                    │
│                                                                 │
│  4. ĐIỀU PHỐI vòng lặp Function Calling                         │
│     User hỏi → Gemini chọn tool → ADK gọi MCP Server            │
│     → nhận kết quả → đưa lại cho Gemini tổng hợp                │
│                                                                 │
│  5. CUNG CẤP giao diện web (adk web)                            │
│     → http://localhost:8000 để chat với agent                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So với bài 02 (viết client thủ công bằng `mcp.ClientSession`), ADK giúp bạn **không phải viết vòng lặp function calling thủ công** nữa. Toàn bộ luồng list_tools → model quyết định → call_tool → model tổng hợp được ADK xử lý tự động.

## Setup

### 1. MCP Server

```bash
cd mcp-server
uv sync

# Set your WeatherAPI key (get one free at https://weatherapi.com)
export WEATHERAPI_KEY="your_weatherapi_key"

# Start the server (runs on port 8085 by default)
uv run python weather.py
```

The server will be available at `http://localhost:8085/mcp`.

### 2. ADK Agent (Client)

```bash
cd mcp-client
uv sync

# Create .env file with your Gemini API key
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env

# Start ADK web interface
uv run adk web
```

Open http://localhost:8000 in your browser, select `weather_agent`, and ask about the weather.

## Configuration

| Variable | Where | Description |
|----------|-------|-------------|
| `WEATHERAPI_KEY` | mcp-server | API key from weatherapi.com |
| `GOOGLE_API_KEY` | mcp-client/.env | Gemini API key |
| `PORT` | mcp-server (env) | Override server port (default: 8085) |

## Testing / Verification

Bạn có thể chạy kịch bản kiểm thử tự động để xác nhận môi trường đã sẵn sàng:
```bash
# Đứng tại thư mục 04-lab
uv run python verify_lab04.py
```

### Checklist Kiểm Thử Thủ Công

**Terminal 1 (Chạy MCP Server):**
```bash
cd mcp-server
export WEATHERAPI_KEY="your_weatherapi_key_here"
uv run python weather.py
```
*(Lưu ý: Nếu không có WEATHERAPI_KEY, server sẽ tự động dùng Mock Data)*

**Terminal 2 (Chạy ADK Web):**
```bash
cd mcp-client
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
uv run adk web
```

**Browser:**
Mở `http://localhost:8000`, chọn `weather_agent` ở góc trên cùng bên trái. Gõ các câu hỏi sau để kiểm tra:

1. **Câu hỏi:** *What's the weather in Brisbane?*
   - **Expected Result:** Agent gọi tool `get_current_weather("Brisbane")` và trả về kết quả thời tiết hiện tại của Brisbane bằng ngôn ngữ thân thiện, kèm theo nhiệt độ (°C).
2. **Câu hỏi:** *Give me a 3-day forecast for Tokyo*
   - **Expected Result:** Agent gọi tool `get_forecast("Tokyo", 3)` và hiển thị dự báo thời tiết 3 ngày tới cho Tokyo (nhiệt độ cao nhất/thấp nhất, khả năng mưa, v.v.).
3. **Câu hỏi:** *Is the MCP server healthy?*
   - **Expected Result:** Agent gọi tool `health_check()` và trả lời rằng server đang hoạt động bình thường (kèm theo thời gian phản hồi và trạng thái API key).
