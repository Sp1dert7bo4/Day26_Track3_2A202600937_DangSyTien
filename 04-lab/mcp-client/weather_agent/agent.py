"""
Weather Agent - Connects to Remote MCP Server on Cloud Run
Successfully connects to custom MCP HTTP endpoints!
"""
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load variables from .env
load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")

logger.info(f"🌐 Initializing weather agent with remote MCP server")
logger.info(f"📡 MCP Server: {MCP_SERVER_URL}")

AGENT_INSTRUCTION = """
Bạn là một trợ lý thời tiết thân thiện và hữu ích.
Hãy LUÔN dùng các công cụ MCP weather tools (get_current_weather, get_forecast) để tra cứu thời tiết khi người dùng hỏi.
- Nếu người dùng không nói rõ thành phố (city), hãy hỏi lại họ.
- Dự báo thời tiết (forecast) chỉ hỗ trợ từ 1 đến 3 ngày. Nếu người dùng hỏi nhiều hơn, hãy thông báo giới hạn này.
- Trả lời thân thiện, ngắn gọn, và luôn kèm theo đơn vị nhiệt độ rõ ràng (°C).
- Nếu công cụ (MCP server) trả về lỗi hoặc không có dữ liệu, hãy thông báo cho người dùng kiểm tra lại MCP Server hoặc API key.
"""

try:
    # Create connection parameters for the remote MCP server
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=30.0,  # Increased timeout for Cloud Run cold starts
    )
    
    # Create the MCP toolset - this will connect to the remote server
    logger.info("🔌 Connecting to MCP server...")
    weather_tools = McpToolset(
        connection_params=connection_params,
    )
    logger.info("✅ MCP toolset created successfully")
    
    # Create the agent with remote MCP tools
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        tools=[weather_tools],
        instruction=AGENT_INSTRUCTION,
    )
    logger.info("✅ Weather agent initialized with remote MCP tools:")
    logger.info("   - get_current_weather(city)")
    logger.info("   - get_forecast(city, days)")
    logger.info("   - health_check()")
    logger.info("🎉 Remote MCP connection successful!")
    
except Exception as e:
    logger.error(f"❌ Failed to connect to remote MCP server: {e}")
    logger.error(f"   Server URL: {MCP_SERVER_URL}")
    import traceback
    traceback.print_exc()
    
    # Create a fallback agent without tools
    logger.warning("⚠️  Creating fallback agent without MCP tools")
    fallback_instruction = """
    Rất tiếc, hiện tại tôi không thể kết nối đến máy chủ thời tiết (MCP Server).
    Vui lòng nhắc người dùng kiểm tra lại MCP Server đã chạy chưa (tại http://localhost:8085/mcp) và cấu hình API Key có đúng không.
    """
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        instruction=fallback_instruction,
    )

