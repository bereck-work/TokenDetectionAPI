from loguru import logger
import asyncio
import uvloop
import sys
from utils.server import Server

if __name__ == "__main__":
    if sys.platform.lower() == "linux":
        logger.info("This app is running on a Linux based operating system. Using uvloop for asyncIO event loop.")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    if sys.platform.lower() == "win32":
        logger.info("This app is running on a Windows based operating system.")
        logger.info("Using a Windows specific event loop.")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    server = Server()
    try:
        server.start_uvicorn_server()
    except KeyboardInterrupt:
        logger.info("[*] User interrupted the program. Shutting down.")
        exit(0)

    except SystemExit:
        logger.info("Shutting down server due to interpreter exit.")
