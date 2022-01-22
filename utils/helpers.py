import asyncio
import datetime
import functools
import json
import typing

import yaml
from loguru import logger
from pydantic import BaseModel


class Config:
    """
    A class to load and store configuration data from a YAML file.
    """

    def __init__(self, file: str = "./config/config.yml"):
        self.logger = logger
        with open(file, encoding="utf-8") as f:
            self.data = yaml.load(f, Loader=yaml.FullLoader)

    @property
    def port(self) -> typing.Optional[int]:
        """
        This property returns the port of the app.


        Returns
        -------
        typing.Optional[int]
            The port defined for the app.
        """
        port = self.data["Settings"]["port"]
        if port is None:
            self.logger.error("Port is not set in the config.yml file.")
            exit(code=1)

        return int(port)

    @property
    def host(self) -> typing.Optional[str]:
        """
        This property returns the host defined for the app.


        Returns
        -------
        str
            The host address.
        """
        data = self.data["Settings"]["host"]
        if data == "":
            self.logger.error("No host found in config.yml")
            exit(code=1)
        return data

    @property
    def preview(self) -> typing.Optional[bool]:
        """
        This property returns the preview mode.


        Returns
        -------
        bool
            The preview mode.
        """
        mode = self.data["Settings"]["preview"]
        if mode is None:
            self.logger.error("Preview mode is not set in the config.yml file.")
            exit(code=1)
        if mode == "true":
            return True
        elif mode == "false":
            return False

    @property
    def redis_address(self) -> typing.Optional[str]:
        """
        This property returns the redis address.


        Returns
        -------
        str
            The redis url.
        """
        data = self.data["Redis"]["address"]
        if data == "":
            self.logger.error("No redis address found in config.yml")
            exit(code=1)
        return data

    @property
    def redis_port(self) -> typing.Optional[int]:
        """
        This property returns the redis port.


        Returns
        -------
        int
            The redis port.
        """
        data = self.data["Redis"]["port"]
        if data == "":
            self.logger.error("No redis port found in config.yml")
            exit(code=1)
        return int(data)

    @property
    def redis_password(self) -> typing.Optional[str]:
        """
        This property returns the redis password.


        Returns
        -------
        str
            The redis password.
        """
        data = self.data["Redis"]["password"]
        if data == "":
            self.logger.error("No redis password found in config.yml")
            exit(code=1)
        return data

    @property
    def redis_db(self) -> typing.Optional[int]:
        """
        This property returns the redis database.


        Returns
        -------
        int
            The redis database.
        """
        data = self.data["Redis"]["database"]
        if data == "":
            self.logger.error("No redis database found in config.yml")
            exit(code=1)
        return int(data)

    @property
    def redis_username(self) -> typing.Optional[str]:
        """
        This property returns the redis username.


        Returns
        -------
        str
            The redis username.
        """
        data = self.data["Redis"]["username"]
        if data == "":
            self.logger.error("No redis username found in config.yml")
            exit(code=1)
        return data

    def __repr__(self):
        return f"<Config {self.data}>"


def executor_function(sync_function: typing.Callable):
    """
    A decorator that wraps a sync function in an executor, changing it into an async function.
    This allows processing functions to be wrapped and used immediately as an async function.

    Parameters
    ----------
    sync_function : typing.Callable
        The function to be wrapped.

    Returns
    -------
    typing.Callable
        The wrapped function as a coroutine.
    """

    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        """
        Asynchronous function that wraps a sync function with an executor.
        """

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper


class Token(BaseModel):
    """
    A class that represents a discord bot token, in its indiviual parts.
    """

    token_string: typing.Union[str, None] = None
    raw_data: typing.Union[str, None] = None
    user_id: typing.Union[str, int, None] = None
    timestamp: typing.Union[int, None] = None
    created_at: typing.Union[datetime.datetime, None] = None
    hmac: typing.Union[str, None] = None
    is_valid: bool
    reason: typing.Union[str, None] = None

    def jsonify(self) -> dict:
        """
        Converts the Token object into a dictionary.

        Returns
        -------
        typing.Dict
            The dictionary representation of the Token object.
        """
        data = {
            "token_string": self.token_string,
            "user_id": self.user_id,
            "raw_data": self.raw_data,
            "timestamp": self.timestamp,
            "created_at": str(self.created_at),
            "hmac": self.hmac,
            "is_valid": self.is_valid,
            "reason": self.reason,
        }
        json_data = json.dumps(data)
        return json.loads(json_data)

    def __repr__(self):
        return f"<TokenData {self.token_string}>"


class ImageRequest(BaseModel):
    """
    A model that represents a POST request to the image endpoint.

    Attributes
    ----------
        The URL of the image to be processed.
    """

    url: str


class TextRequest(BaseModel):
    """
    A model that represents a POST request to the text endpoint.

    Attributes
    ----------
        The text to be processed.
    """

    content: str
