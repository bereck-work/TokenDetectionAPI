from loguru import logger
import asyncio
import uvloop
import sys
from utils.process import Process

if __name__ == "__main__":
    if sys.platform.lower() == "linux":
        logger.info("Linux based operating system detected!")
        logger.info("Using uvloop for asyncio!")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    if sys.platform.lower() == "win32":
        logger.info("Windows based operating system detected!")
        logger.info("Using special Windows Event Loop!")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    process = Process()
    try:
        process.start_uvicorn_server()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        exit(0)

    except SystemExit:
        logger.info("Shutting down server...")
