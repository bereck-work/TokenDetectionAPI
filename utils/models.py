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

    token_string: typing.Optional[str] = None
    raw_data: typing.Optional[str] = None
    user_id: typing.Optional[int] = None
    timestamp: typing.Optional[int] = None
    created_at: typing.Optional[datetime.datetime] = None
    hmac: typing.Optional[str] = None
    is_valid: bool
    reason: typing.Optional[str] = None

    def jsonify(self) -> dict:
        """
        This method converts the Token object into a regular python dictionary object.

        Returns:
            (dict): The dictionary representation of the Token object.
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

    Attributes:
        The URL of the image to be processed.
    """

    url: str


class TextRequest(BaseModel):
    """
    A model that represents a POST request to the text endpoint.
    **api/token/text**
    **api/ocr/text**

    Attributes:
        The text to be processed.
    """

    content: str


class OCRData(BaseModel):
    """
    A model that represents the response from the OCR endpoint, both, from the text endpoint and from the image endpoint.

    **api/token/text**
    **api/ocr/text**

    Attributes:
        The text that was processed.
    """

    url: str
    unfiltered_text: str
    filtered_text: str
