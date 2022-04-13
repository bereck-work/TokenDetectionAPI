import datetime
import json
import typing

from pydantic import BaseModel

__all__ = (
    "Token",
    "ImageRequest",
    "OCRData",
    "TextRequest",
)


class Token(BaseModel):
    """
    A class that represents a discord bot token, in its indiviual parts.
    """

    token_string: typing.Union[str, None] = None
    raw_data: typing.Union[str, None] = None
    user_id: typing.Union[int, None] = None
    timestamp: typing.Union[int, None] = None
    created_at: typing.Union[datetime.datetime, None] = None
    hmac: typing.Union[str, None] = None
    is_valid: bool
    reason: typing.Union[str, None] = None

    def jsonify(self) -> dict:
        """
        This method converts the Token object into a regular python dictionary object.

        Returns
        -------
        dict
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
        data = json.loads(json_data)
        return data

    def __repr__(self):
        return f"<Token {self.jsonify()}>"


class ImageRequest(BaseModel):
    """
    A model that represents a POST request to the image endpoint.
    **api/token/image**
    **api/ocr/text**

    Attributes
    ----------
        The URL of the image to be processed.
    """

    url: str


class TextRequest(BaseModel):
    """
    A model that represents a POST request to the text endpoint.
    **api/token/text**
    **api/ocr/text**

    Attributes
    ----------
        The text to be processed.
    """

    content: str


class OCRData(BaseModel):
    """
    A model that represents the response from the OCR endpoint, both, the text and the image.

    Attributes
    ----------
        The text that was processed.
    """

    url: str
    unfiltered_text: str
    filtered_text: str
