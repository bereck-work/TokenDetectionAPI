from loguru import logger

from utils.process import Process

if __name__ == "__main__":
    process = Process()
    try:
        process.start_server()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        exit(0)
