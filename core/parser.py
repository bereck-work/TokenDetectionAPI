import base64
import re
import typing
from datetime import datetime, timezone

from loguru import logger

from utils.helpers import Token


class TokenParser:
    """
    A class that parses a discord bot token.
    """

    def __init__(self):
        self.token_string = typing.AnyStr
        self.token_epoch = 1_293_840_000
        self.discord_epoch = 1_420_070_400
        self.discord_bot_token_regex = re.compile(
            r"([a-z0-9_-]{23,28})\.([a-z0-9_-]{6,7})\.([a-z0-9_-]{27})", re.IGNORECASE
        )  # regex for discord bot token, taken from https://github.com/onerandomusername/secrets-pre-commit
        # thanks arl!

    @staticmethod
    def get_timestamp(timestamp: str) -> typing.Optional[int]:
        """
        This method returns the timestamp of the token.

        Parameters
        ----------
            timestamp (typing.AnyStr): The timestamp of the token encoded in base64.

        Returns
        -------
            typing.Optional[int]:
               The timestamp of the token as an integer.
        """
        try:
            data = int.from_bytes(base64.urlsafe_b64decode(timestamp + "=="), "big")
            return data
        except ValueError:
            logger.error(f"Could not decode timestamp: {timestamp}")
            return None

    @staticmethod
    def created_at(timestamp: int) -> typing.Optional[datetime]:
        """
        This method returns the created at date of the token.

        Parameters
        -----------
            timestamp
                The timestamp of the token.

        Returns
        -------
            typing.Optional[datetime.datetime]
                The created at date of the token.
        """
        try:
            time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return time
        except Exception as e:
            logger.error(f"Error while decoding timestamp: {e}")
            return None

    @staticmethod
    def get_user_id(user_id: typing.AnyStr) -> typing.Optional[int]:
        """
        This method returns the user ID of the token.

        Args:
            user_id (typing.AnyStr): The user ID of the token.

        Returns:
            int: The user ID of the token.
        """
        try:
            data = int(base64.urlsafe_b64decode(user_id))
            return data
        except ValueError:
            logger.error(
                f"Could not decode user ID: {user_id}, as it is not a valid base64 encoded string."
            )
            return None

    @staticmethod
    def get_hmac(hmac: str) -> typing.Optional[str]:
        """
        This method returns the hmac of the token.

        Parameters
        ----------
            hmac (typing.AnyStr): The hmac of the token.

        Returns
        -------
            str:
                The hmac of the token.
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
        self, raw_data=typing.AnyStr, data_parsed_from_type: typing.AnyStr = None
    ) -> Token:
        """
        This method that returns various parts of the discord bot token, information about the token and validates it.
        It uses regex to match if there is a token like string in string, and then it splits the token into its parts,
        if a match is found.

        Parameters
        ----------
            raw_data : typing.AnyStr
                The raw data that needs to be parsed.

            data_parsed_from_type : typing.AnyStr
                The data that the raw data was parsed from.
                If the raw data was extracted from an image, then it would be "image", if it was extracted from a raw text
                file, then it would be "text".

            # Laziness

        Returns
        -------
        Token
            A discord bot token object.
        """
        for match in self.discord_bot_token_regex.finditer(raw_data):
            data = match.group(1), match.group(2), match.group(3)
            user_id = self.get_user_id(data[0])
            timestamp = self.get_timestamp(data[1])
            hmac = self.get_hmac(data[2])
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
                    "the components are invalid, if it looks like a token, it reports it as valid."
                    "Please note that this is not a guarantee that the token is valid, and this is a stupid "
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
                reason="This token is invalid, as it does not match the discord bot token format.",
                raw_data=raw_data,
            )

    def __repr__(self):
        return f"<TokenParser: {self.token_string}>"

    @property
    def epoch_of_discord(self):
        """
        This property returns the Discord epoch.

        Returns
        -------
        int
            Discord epoch.
        """
        return self.discord_epoch

    @property
    def epoch_of_token(self):
        """
        This property returns the Token epoch.
        """
        return self.token_epoch

    @property
    def token(self):
        """
        This property returns the token, that was read from the image.
        """
        return self.token_string
