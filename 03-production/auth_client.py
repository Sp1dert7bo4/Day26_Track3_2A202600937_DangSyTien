"""MCP Client có Authentication — kết nối tới auth_server.py qua HTTP.

Client truyền bearer token thông qua httpx.AsyncClient. MCP SDK tự gắn
token vào mọi request HTTP (POST, GET, DELETE) tới server.

Cách chạy (cần auth_server.py đang chạy ở terminal khác):
    cd 03-production
    python auth_server.py            # terminal 1
    python auth_client.py            # terminal 2
"""

from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SERVER_URL = "http://localhost:8001/mcp"
VALID_TOKEN = "demo-secret-token"

async def test_auth(case_name: str, token: str | None = None) -> None:
    print(f"\n{'='*40}")
    print(f"Test Case: {case_name}")
    print(f"{'='*40}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    http_client = httpx.AsyncClient(headers=headers)
    
    try:
        async with http_client:
            async with streamable_http_client(SERVER_URL, http_client=http_client) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    print(f"Thành công! Khám phá được {len(tools.tools)} tools.")
                    result = await session.call_tool("get_weather", {"city": "Hanoi"})
                    print(f"Kết quả gọi tool: {result.content[0].text}")
    except httpx.HTTPStatusError as e:
        print(f"Lỗi HTTP: {e.response.status_code} - {e.response.reason_phrase}")
    except Exception as e:
        if "401" in str(e):
            print("Lỗi HTTP: 401 - Unauthorized (Thiếu Token)")
        elif "403" in str(e):
            print("Lỗi HTTP: 403 - Forbidden (Sai Token)")
        else:
            print(f"Lỗi: {type(e).__name__} - {e}")
            if type(e).__name__ == "ExceptionGroup":
                for sub_e in e.exceptions:
                    print(f"  Sub-exception: {type(sub_e).__name__} - {sub_e}")
                    if hasattr(sub_e, 'response'):
                        print(f"  HTTP Lỗi: {sub_e.response.status_code}")

async def main() -> None:
    # 1. Thiếu token
    await test_auth("Thiếu Token (Expected: 401 Unauthorized)", None)
    
    # 2. Sai token
    await test_auth("Sai Token (Expected: 403 Forbidden)", "wrong-token-123")
    
    # 3. Token đúng
    await test_auth("Token hợp lệ (Expected: Thành công)", VALID_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
