import subprocess
import sys
from threading import Thread

import uvicorn
from loguru import logger

from utils.helpers import Config


class Process:
    """
    A class that handles the process of running the server.
    """

    def __init__(self):
        self.config = Config()
        self.logger = logger
        self.ngrok_command = f"ngrok http {self.config.host}:{self.config.port}"
        self.baseprogram = "ngrok"

    def check_if_ngrok_exists(self) -> bool:
        """
        This method checks if ngrok is installed on the system.

        Returns:
            bool: True if ngrok is installed, False otherwise.
        """
        process = subprocess.run(
            ["which", self.baseprogram], capture_output=True, text=True
        )
        if process.returncode == 0:
            location = process.stdout
            self.logger.info(f"{self.baseprogram} exists!,  located at {location}")
            return True
        else:
            self.logger.error(
                f"{self.baseprogram} does not exist!. "
                f"Please install {self.baseprogram} to run this app in preview mode."
            )
            return False

    def check_preview_mode(self) -> bool:
        """
        This method checks if the preview mode is enabled.

        Returns
        -------
        bool
            True if preview mode is enabled, False otherwise.
        """
        if self.config.preview:
            self.logger.info(
                "Preview mode is enabled. A ngrok tunnel will be created for this session and "
                "will portfoward the localhost server.\nTo be able to view the API, please open "
                "https://dashboard.ngrok.com/endpoints/status in your browser, and click on one "
                "of the links that has been created. This feature should not be used in production."
            )
            return True
        else:
            self.logger.info(
                "Preview mode is disabled. Ngrok tunnel will not be started and the API will be "
                "available only on localhost."
            )
            return False

    def start_ngrok(self):
        """
        This method starts ngrok.
        """
        result = self.check_if_ngrok_exists()
        if result:
            self.logger.info(
                f"Starting {self.baseprogram} tunnel to {self.config.host}:{self.config.port}"
            )
            ngrok_process = subprocess.run(
                self.ngrok_command,
                capture_output=True,
                text=True,
                shell=True,
            )
            if ngrok_process.returncode == 0:
                self.logger.success(
                    f"{self.baseprogram} tunnel started successfully. {ngrok_process.stdout}"
                )
            if ngrok_process.returncode == -2:
                return  # signal means SIGKILL aka the process was killed.
            else:
                self.logger.error(
                    f"{self.baseprogram} tunnel failed to start. Error: {ngrok_process.stdout}"
                )
                sys.exit(1)
        else:
            return

    def start_uvicorn(self):
        """
        This method starts the uvicorn server.
        """
        self.logger.info(
            f"Started uvicorn server at http://{self.config.host}:{self.config.port}"
        )
        uvicorn.run("src.endpoints:app", host=self.config.host, port=self.config.port)

    def start_server(self):
        """
        This method starts the uvicorn server.
        """
        self.logger.info("Starting server....")
        result_for_preview_mode = self.check_preview_mode()
        uvicorn_thread = Thread(target=self.start_uvicorn)
        ngrok_thread = Thread(target=self.start_ngrok)
        if result_for_preview_mode is True:
            ngrok_thread.start()
            uvicorn_thread.start()
            uvicorn_thread.join()
            ngrok_thread.join()
        else:
            Thread(target=self.start_uvicorn()).start()
