import asyncio
import functools
import sys
import typing

import yaml
from loguru import logger

__all__ = (
    "Config",
    "executor_function",
)


class Config:
    """
    A class to load and store configuration data from a YAML file.
    """

    def __init__(self):
        self.logger = logger
        self.config_file_path = "./config/config.yml"
        with open(self.config_file_path, encoding="utf-8") as f:
            self.data = yaml.load(f, Loader=yaml.FullLoader)

    @property
    def port(self) -> typing.Optional[int]:
        """
        This property returns the port of the app that is defined in the configuration file.

        Returns:
            (typing.Optional[int]): The port defined for the app.
        """
        port = self.data["Settings"]["port"]
        if port is None:
            self.logger.error("Port is not set in the config.yml file.")
            sys.exit()

        return int(port)

    @property
    def host(self) -> typing.Optional[str]:
        """
        This property returns the host defined for the app.

        Returns:
            (typing.Optional[str]): The host defined for the app.
        """
        data = self.data["Settings"]["host"]
        if data is None:
            self.logger.error("No host found in config.yml")
            sys.exit(1)
        return data

    @property
    def preview(self) -> typing.Optional[bool]:
        """
        This property returns the state of preview mode setting in the config.yml file.

        Returns:
            (typing.Optional[bool]): True if preview mode is enabled, False otherwise.
        """
        mode = self.data["Settings"]["preview"]
        if mode is None:
            self.logger.error("Preview setting is not set in the config.yml file.")
            sys.exit(1)
        if mode is not True and mode is not False:
            self.logger.error(
                "Invalid choice for preview mode in the config.yml file. Accepted values are 'on' or 'off'."
            )
            sys.exit(1)
        return mode

    @property
    def fastapi_debug_mode(self) -> typing.Optional[bool]:
        """
        This property returns the state of fastapi debug mode setting in the config.yml file.

        Returns:
            (bool): The fastapi debug mode.
        """
        mode = self.data["Settings"]["debug"]
        if mode is None:
            self.logger.error("Fastapi debug mode is not set in the config.yml file.")
            sys.exit(1)
        if mode is not True and mode is not False:
            self.logger.error(
                "Invalid choice for preview mode in the config.yml file. Accepted values are 'on' or 'off'."
            )
            sys.exit(1)
        return mode

    @property
    def redis_address(self) -> typing.Optional[str]:
        """
        This property returns the redis address defined in the config.yml file.

        Returns:
            (typing.Optional[str]): The redis address.
        """
        data = self.data["Redis"]["address"]
        if data is None:
            self.logger.error("Redis address was not set in config.yml")
            sys.exit(1)
        return data

    @property
    def redis_port(self) -> typing.Optional[int]:
        """
        This property returns the redis port defined in the config.yml file.

        Returns:
            (typing.Optional[int]): The redis port.
        """
        data = self.data["Redis"]["port"]
        if data is None:
            self.logger.error("Redis port was not set in config.yml")
            sys.exit(1)
        return int(data)

    @property
    def redis_password(self) -> typing.Optional[str]:
        """
        This property returns the redis user password defined in the config.yml file.

        Returns:
            (typing.Optional[str]): The redis user password.
        """
        data = self.data["Redis"]["password"]
        if data is None:
            self.logger.error("Redis password is not provided in config.yml")
            sys.exit(1)
        return data

    @property
    def redis_db(self) -> typing.Optional[int]:
        """
        This property returns the redis database index defined in the config.yml file.

        Returns:
            (typing.Optional[int]): The redis database index.
        """
        data = self.data["Redis"]["database"]
        if data is None:
            self.logger.error("Redis database index not provided in config.yml")
            sys.exit(1)
        return int(data)

    @property
    def redis_username(self) -> typing.Optional[str]:
        """
        This property returns the redis username that is defined in the config.yml file.

        Returns:
            (typing.Optional[str]): The redis username.
        """
        data = self.data["Redis"]["username"]
        if data == "":
            self.logger.error("No redis username found in config.yml")
            sys.exit(1)
        return data

    def __repr__(self):
        return f"<Config {self.data}>"


def executor_function(
    sync_function: typing.Callable[..., typing.Callable]
):
    # Taken from Jishaku ( https://github.com/Gorialis/jishaku/blob/master/jishaku/functools.py#L20 )
    """
    A decorator that wraps a sync function in an executor, changing it into an async function.
    This allows processing functions to be wrapped and used immediately as an async function.

    Parameters:
        sync_function (typing.Callable): This parameter takes the function to be wrapped and converts it into an
                                         async function.


    Returns:
        (typing.Callable): The wrapped function as a coroutine.

    Raises:
        (TypeError): If the function object that is passed is already an async function.
    """

    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        """
        Asynchronous function that wraps a sync function with an executor.
        """

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        if asyncio.iscoroutinefunction(internal_function):
            raise TypeError(
                f"This decorator only wraps and converts a synchronous function into an async function, "
                f"{sync_function} is already an async function."
            )
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper
