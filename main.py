import asyncio
import sys

import uvicorn

from app.api.v1.logging import API_LOG_CONFIG

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    uvicorn.run(
        "app.asgi:app",
        host="127.0.0.1",
        port=8000,
        loop="asyncio",
        log_config=API_LOG_CONFIG
    )
