# Lab 04 — Weather Agent with Remote MCP Server

## 🎯 1. Mục tiêu (Objectives)
Lab này được thiết kế để giúp bạn hiểu rõ bản chất và cách vận hành của các thành phần sau:
- **Hiểu Function Calling:** Model quyết định gọi hàm, còn việc thực thi hàm do môi trường (ứng dụng) đảm nhiệm.
- **Hiểu MCP (Model Context Protocol):** Giao thức chuẩn hóa để kết nối AI Models với các công cụ (tools) và dữ liệu (context) bên ngoài.
- **Hiểu ADK (Agent Development Kit):** Đóng vai trò là một **MCP Client** điều phối thông minh giữa LLM và Server.
- **Xây dựng MCP Weather Server Remote:** Sử dụng FastMCP để tạo server xử lý dữ liệu thời tiết.
- **Tích hợp:** Agent sử dụng trực tiếp các MCP tools qua giao thức **Streamable HTTP**.

---

## 🏗️ 2. Architecture Diagram

Luồng hoạt động của hệ thống từ lúc người dùng đặt câu hỏi đến khi nhận được dữ liệu thời tiết:

```text
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  User Browser   │ ────▶ │   ADK Web UI    │ ────▶ │  Weather Agent  │ ────▶ │   MCP Server    │ ────▶ │  WeatherAPI.com  │
│ (localhost:8000)│ ◀──── │ (mcp-client)    │ ◀──── │ (McpToolset)    │ ◀──── │ (localhost:8085)│ ◀──── │ (External API)   │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘       └──────────────────┘
```

---

## 📂 3. Project Structure

Dự án được chia thành các phần tiến trình học tập và ứng dụng thực tế:

```
📦 Day26_Track3_2A202600937_DangSyTien
 ┣ 📂 01-function-calling/    # Minh họa Function Calling thuần bằng Gemini SDK
 ┣ 📂 02-mcp-basics/          # Demo MCP cơ bản (stdio transport) không cần API key
 ┣ 📂 03-production/          # Demo MCP nâng cao: Auth, Tool Registry, Versioning
 ┣ 📂 04-lab/                 # Chứa toàn bộ Lab 04 Weather Agent (bao gồm client và server)
 ┃ ┣ 📂 mcp-server/           # MCP Server cung cấp tools thời tiết qua HTTP
 ┃ ┗ 📂 mcp-client/           # ADK Agent (Client) tích hợp và điều phối
 ┣ 📜 .env.example            # Mẫu file chứa biến môi trường
 ┗ 📜 README.md               # Tài liệu tổng hợp (file này)
```

---

## ⚙️ 4. Setup (Cài đặt)

### Yêu cầu trước khi bắt đầu
- Bạn có thể sử dụng `uv` (khuyên dùng vì tốc độ siêu nhanh) hoặc `pip` để quản lý môi trường.
- Đăng ký API Key tại [WeatherAPI](https://www.weatherapi.com/) (để lấy dữ liệu thời tiết thực).
- Đăng ký Google API Key tại [Google AI Studio](https://aistudio.google.com/) (để dùng Gemini LLM).

### Khởi tạo biến môi trường
Tạo một file `.env` ở thư mục gốc của project (có thể copy từ `.env.example`):
```bash
cp .env.example .env
```
Mở file `.env` và điền thông tin:
```env
WEATHERAPI_KEY=your_weatherapi_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```
*(Đảm bảo file `.env` đã được thêm vào `.gitignore` để không bao giờ bị commit lên Git).*

---

## 🚀 5. Hướng dẫn chạy (How to run)

Hệ thống yêu cầu chạy song song **Server** và **Client** ở 2 terminal khác nhau.

### Terminal 1: Chạy MCP Server
Server này sẽ chạy ở nền và mở cổng 8085, đóng vai trò cung cấp tools thời tiết cho bất cứ MCP Client nào.
```bash
cd 04-lab/mcp-server
uv sync
export WEATHERAPI_KEY="your_weatherapi_key_here"  # Tùy chọn nếu chưa ghi vào .env
uv run python weather.py
```
*Lưu ý: Nếu không có WEATHERAPI_KEY, server sẽ tự động trả về Mock Data (dữ liệu giả lập).*

### Terminal 2: Chạy ADK Client
Client này chứa giao diện Web và Agent điều phối Gemini LLM.
```bash
cd 04-lab/mcp-client
uv sync
# Chắc chắn GOOGLE_API_KEY đã có trong môi trường
uv run adk web
```

---

## 💻 6. Cách sử dụng (Usage)

1. Mở trình duyệt và truy cập: [http://localhost:8000](http://localhost:8000)
2. Ở góc trên cùng bên trái giao diện, nhấn vào menu chọn Agent và chọn **`weather_agent`**.
3. Bắt đầu chat với Agent bằng các câu hỏi thời tiết tự nhiên!

---

## 🛠️ 7. Danh sách MCP Tools

MCP Server expose 3 tools thông qua giao thức Streamable HTTP:
1. `get_current_weather(city: str)`: Lấy dữ liệu thời tiết hiện hành theo thời gian thực (nhiệt độ, độ ẩm, sức gió,...).
2. `get_forecast(city: str, days: int)`: Lấy dự báo thời tiết trong `days` ngày tới.
3. `health_check()`: Kiểm tra tình trạng hoạt động của MCP Server và API Key.

---

## 💬 8. Example Prompts

Bạn có thể thử nhập các câu hỏi sau vào giao diện Web của ADK:

- *"What's the weather in Brisbane?"*
- *"Give me a 3-day forecast for Tokyo."*
- *"Is the weather MCP server healthy?"*
- *"Should I bring an umbrella in Hanoi today?"*

---

## ⚠️ 9. Troubleshooting (Khắc phục sự cố)

| Sự cố / Lỗi | Nguyên nhân & Cách khắc phục |
|-------------|------------------------------|
| **Thiếu WEATHERAPI_KEY** | Code đã được tích hợp tính năng Mock Data tự động. Tuy nhiên, nếu bạn muốn dữ liệu thật, hãy đăng ký key ở weatherapi.com và truyền vào `.env` hoặc `export WEATHERAPI_KEY=...` |
| **Thiếu GOOGLE_API_KEY** hoặc **Lỗi 403 Permission Denied** | Thiếu key hoặc API key của bạn bị chặn IP (IP address restriction) trên Google Cloud. Hãy tạo một key mới hoàn toàn trên AI Studio (không giới hạn IP) và thêm vào file `.env`. |
| **Lỗi Connection / MCP server chưa chạy** | Đảm bảo Terminal 1 đang chạy `weather.py`. Nếu bạn tắt terminal này, ADK sẽ báo lỗi kết nối. |
| **Sai Port 8085** | Nếu port bị trùng, bạn có thể truyền biến `PORT=9000` trước lệnh chạy server. Sau đó vào file `agent.py` của client để sửa lại đường dẫn `StreamableHTTPConnectionParams`. |
| **ADK web không thấy agent** | Hãy kiểm tra xem bạn đã chạy `uv run adk web` đúng thư mục `04-lab/mcp-client` chưa. ADK tự tìm agent trong thư mục đang đứng. |
| **WeatherAPI Quota / Rate Limit** | Tài khoản free của WeatherAPI có giới hạn. Đợi 1 thời gian hoặc đổi API key mới nếu bị khóa limit. |

---

## 🎬 10. Demo Video Script (2 phút)

Nếu bạn cần quay video demo nộp bài, hãy tham khảo kịch bản 2 phút sau:

- **0:00 - 0:15:** Giới thiệu ngắn gọn kiến trúc hệ thống: "*Đây là Weather Agent với ADK đóng vai trò Client, kết nối HTTP tới MCP Server để lấy dữ liệu từ WeatherAPI.*"
- **0:15 - 0:35:** Mở Terminal 1, gõ lệnh chạy MCP Server (`uv run python weather.py`). Cho thấy log server báo khởi động thành công trên cổng 8085.
- **0:35 - 0:50:** Mở Terminal 2, chạy ADK Web (`uv run adk web`).
- **0:50 - 1:10:** Mở browser `localhost:8000`, chọn `weather_agent`, nhập lệnh: *"Is the weather MCP server healthy?"* để test tool `health_check`.
- **1:10 - 1:30:** Test tool `get_current_weather` bằng cách nhập: *"What's the weather in Brisbane?"*. Show màn hình trả về nhiệt độ.
- **1:30 - 1:45:** Test tool `get_forecast` bằng cách nhập: *"Give me a 3-day forecast for Tokyo."*
- **1:45 - 2:00:** Tổng kết nhanh lại bài học cốt lõi: *"Agent không hề biết thời tiết, nó chỉ là một LLM Client thông minh tự động điều hướng sang MCP Server để thực thi tool và lấy dữ liệu"* và kết thúc video.

---

## ✅ 11. Checklist Nộp Bài

- [x] Code đã chạy mượt mà (Pass cả 01, 02, 03 và 04-lab).
- [x] File `README.md` rõ ràng, có hướng dẫn đầy đủ từng bước.
- [x] Có file `.env.example` cung cấp sẵn template biến môi trường.
- [x] KHÔNG bị lộ (commit) API Key thật lên Github.
- [x] Có Troubleshooting để hỗ trợ fix lỗi dễ dàng.
- [ ] Có Screenshot hoặc Video Demo đính kèm (Bạn cần tự quay/chụp màn hình).
