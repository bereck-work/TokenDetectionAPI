import base64
import re
import typing
from datetime import datetime, timezone
from typing import Callable, Optional

from loguru import logger

from utils.models import Token

__all__ = ("TokenParser",)


class TokenParser:
    """
    A class that parses a discord bot token into its individual components and returns various information about it in
    class :class:`Token` object.
    """

    def __init__(self):
        self.token_string = str()
        self.token_epoch = 1_293_840_000
        self.discord_epoch = 1_420_070_400
        self.discord_bot_token_regex = re.compile(
            r"([a-z0-9_-]{23,28})\.([a-z0-9_-]{6,7})\.([a-z0-9_-]{27})", re.IGNORECASE
        )  # regex for discord bot token, taken from https://github.com/onerandomusername/secrets-pre-commit
        # thanks arl!

    def get_timestamp(self, timestamp: str) -> typing.Optional[int]:
        """
        This method takes a timestamp as a string and then returns the date and time of when the token was created,
        based on the timestamp, if the timestamp is valid.

        Parameters:
            timestamp (str): This parameter takes the timestamp of the token as a string.

        Returns:
            (typing.Optional[int]): The date and time of when the token was created.
        """
        try:
            data = int.from_bytes(
                base64.urlsafe_b64decode(timestamp + "=="), byteorder="big"
            )
            if data + self.token_epoch < self.discord_epoch:
                logger.error(
                    f"Invalid token timestamp: {data}, as the sum of timestamp and token epoch is smaller "
                    f"than the Discord epoch."
                )
                return None
            return data
        except ValueError:
            logger.error(f"Could not decode timestamp: {timestamp}")
            return None

    @staticmethod
    def created_at(timestamp: int) -> typing.Optional[datetime]:
        """
        This method returns a datetime object of a timestamp. This method is just a utility method, that is called
        by :meth:`get_timestamp` and :meth:`validate_token`.

        Parameters:
            timestamp (int): This parameter takes a timestamp as an integer.

        Returns:
            (typing.Optional[datetime.datetime]): The created at date of the token.
        """
        try:
            datetime_extracted_from_timestamp = datetime.fromtimestamp(
                timestamp, tz=timezone.utc
            )
            return datetime_extracted_from_timestamp
        except Exception as e:
            logger.error(f"Error while decoding timestamp: {e}")
            return None

    @staticmethod
    def get_user_id(data: str) -> typing.Optional[int]:
        """
        This method returns the user id from the discord bot token by decoding the base64 string that represents the
        user ID in the token. If the base64 string is valid, it will return an integer that represents the user ID,
        if not it will return None.

        Parameters:
            data (str): This parameter takes the base64 string that represents the user ID in the token.

        Returns:
            (typing.Optional[int]): The user ID of the token as an integer.
        """
        try:
            decoded_base64_data = int(base64.urlsafe_b64decode(data))
            return decoded_base64_data
        except ValueError:
            logger.error(
                f"Could not decode user ID: {data}, as it is not a valid base64 encoded string."
            )
            return None

    @staticmethod
    def validate_hmac_uniqueness(hmac: str) -> typing.Optional[str]:
        """
        This method takes a hmac string and checks if it is unique. If it is unique, it will return the hmac string,
        if not it will return None.

        Parameters:
            hmac (str): This parameter takes hmac of a token as a string.

        Returns:
            (typing.Optional[str]): The hmac of the token as a string if it is unique.
        """
        unique = len(set(hmac.lower()))
        if unique > 3:
            return hmac
        else:
            logger.error(
                f"Could not decode hmac: {hmac}, as it has less than 3 unique characters."
            )
            return None

    async def validate_token(
        self, raw_data: str, data_parsed_from_type: str = None
    ) -> Token:
        """
        This method that returns various parts of the discord bot token, information about the token and validates it.
        It uses regex to match if there is a token like string in string, and then it splits the token into its parts,
        if a match is found.

        Parameters:
            raw_data (str): This parameter takes the raw text data as a string that needs to be parsed.

            data_parsed_from_type (str): This parameter takes the type of data that is parsed from the raw data.
                                         If the text was extracted from an image, then it would be "image",
                                         if it was extracted directly from text, then it would be "text".
            # Laziness

        Returns:
            (Token): The token object containing all the data extracted from the token.
        """
        for match in self.discord_bot_token_regex.finditer(raw_data):
            data = match.group(1), match.group(2), match.group(3)
            user_id = self.get_user_id(data[0])
            timestamp = self.get_timestamp(data[1])
            hmac = self.validate_hmac_uniqueness(data[2])
            created_at = self.created_at(timestamp)
            if user_id and timestamp and hmac and data_parsed_from_type == "text":
                #  This if statements checks that, if the data was parsed from raw text and not an image,
                #  and if the token that was found is valid, it reports it as a valid token.
                # This might look stupid at first, but I am lazy.
                return Token(
                    user_id=user_id,
                    hmac=hmac,
                    created_at=created_at,
                    timestamp=timestamp,
                    token_string=".".join(data),
                    is_valid=True,
                    reason="This token is valid, as all components of the token are valid.",
                    raw_data=raw_data,
                )
            if (
                user_id is None
                and timestamp
                and hmac
                and data_parsed_from_type == "image"
            ):
                # This if statement checks that if the token was parsed from an image, and if the token is valid,
                # it reports it as a valid token.
                return Token(
                    user_id=user_id,
                    hmac=hmac,
                    created_at=created_at,
                    timestamp=timestamp,
                    token_string=".".join(data),
                    is_valid=True,
                    reason="This token is invalid, as one or more components of the token are invalid. "
                    "However, it was parsed from an image, and the OCR will not be 100% accurate, so even if "
                    "the components are invalid, if a token like string matches, it is valid. "
                    "Please note that this is not a guarantee that the token is actually valid, and this is a stupid "
                    "solution.",
                    raw_data=raw_data,
                )
            if user_id and timestamp and hmac and data_parsed_from_type == "image":
                return Token(
                    user_id=user_id,
                    hmac=hmac,
                    created_at=created_at,
                    timestamp=timestamp,
                    token_string=".".join(data),
                    is_valid=True,
                    reason="This token is valid, as all components of the token are valid.",
                    raw_data=raw_data,
                )

            else:
                return Token(
                    user_id=user_id,
                    hmac=hmac,
                    created_at=created_at,
                    timestamp=timestamp,
                    token_string=".".join(data),
                    is_valid=False,
                    reason="This token is invalid, as one or more components of the token are invalid.",
                    raw_data=raw_data,
                )
        else:
            return Token(
                is_valid=False,
                reason="No token like string in the extracted text data.",
                raw_data=raw_data,
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.token_string}>"

    @property
    def epoch_of_discord(self) -> int:
        """
        This property returns the Discord epoch.
        """
        return self.discord_epoch

    @property
    def epoch_of_token(self) -> int:
        """
        This property returns the Token epoch.
        """
        return self.token_epoch

    @property
    def token(self) -> str:
        """
        This property returns the token, that was read from the image.
        """
        return self.token_string

    @property
    def token_created_at(self) -> Callable[[int], Optional[datetime]]:
        """
        This property returns the time the token was created.
        """
        return self.created_at
