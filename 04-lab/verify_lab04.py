import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn để có thể import
LAB_DIR = Path(__file__).parent.absolute()
sys.path.append(str(LAB_DIR / "mcp-server"))
sys.path.append(str(LAB_DIR / "mcp-client"))

def print_step(msg: str):
    print(f"\n[🔄] {msg}")

def print_success(msg: str):
    print(f"  ✅ {msg}")

def print_warning(msg: str):
    print(f"  ⚠️ {msg}")

def print_error(msg: str):
    print(f"  ❌ {msg}")

def main():
    print("="*50)
    print(" VERIFICATION SCRIPT - LAB 04 WEATHER AGENT")
    print("="*50)

    # 1. Load .env
    print_step("Loading environment variables from root .env")
    env_path = LAB_DIR.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print_success("Loaded root .env file")
    else:
        print_warning("No .env file found in root directory")

    # 2. Check API Keys
    print_step("Checking API Keys")
    weather_key = os.getenv("WEATHERAPI_KEY")
    if weather_key:
        print_success("WEATHERAPI_KEY is set")
    else:
        print_error("WEATHERAPI_KEY is missing!")
        
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        print_success("GOOGLE_API_KEY is set")
    else:
        print_warning("GOOGLE_API_KEY is missing! ADK Web agent will fail, but you can still run the MCP Server.")

    # 3. Check MCP_SERVER_URL
    print_step("Checking MCP_SERVER_URL")
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")
    if mcp_url == "http://localhost:8085/mcp":
        print_success(f"MCP_SERVER_URL is correct: {mcp_url}")
    else:
        print_warning(f"MCP_SERVER_URL is custom: {mcp_url}")

    # 4. Check imports
    print_step("Checking code imports")
    try:
        import weather
        print_success("Successfully imported mcp-server/weather.py")
    except ImportError as e:
        print_error(f"Failed to import weather.py: {e}")

    try:
        from weather_agent import agent
        print_success("Successfully imported mcp-client/weather_agent/agent.py")
    except ImportError as e:
        if "google.adk" in str(e):
            print_warning("Could not import agent.py because 'google-adk' is not installed in the current environment. This is expected if running outside mcp-client/.venv.")
        else:
            print_error(f"Failed to import agent.py: {e}")

    # 5. Smoke test MCP Server
    print_step("Testing MCP Server connection")
    try:
        # FastMCP streamable-http uses POST /mcp for tool calls.
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "health_check",
                "arguments": {}
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = httpx.post(mcp_url, json=payload, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            print_success("MCP Server is running and reachable!")
            print_success(f"health_check response: {response.text}")
        elif response.status_code in [404, 405, 406]:
            print_success("MCP Server is reachable (Port is open), but returned HTTP " + str(response.status_code))
            print_success("This is expected if the protocol requires specific headers or GET initialization.")
        else:
            print_warning(f"MCP Server returned status code {response.status_code}")
            
    except httpx.ConnectError:
        print_error("MCP Server is NOT running or unreachable at " + mcp_url)
        print("\n" + "="*50)
        print("INSTRUCTIONS TO START MCP SERVER:")
        print("Mở một terminal mới và chạy các lệnh sau:")
        print("  cd mcp-server")
        print("  export WEATHERAPI_KEY=your_key_here")
        print("  uv run python weather.py")
        print("="*50)
    except Exception as e:
        print_error(f"Error connecting to MCP server: {e}")

    print("\nVerification completed.")

if __name__ == "__main__":
    main()
