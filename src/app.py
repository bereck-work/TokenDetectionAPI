import typing
from io import BytesIO

import aiohttp
import fastapi
import pytesseract
from fastapi import FastAPI
from loguru import logger
from fastapi.responses import JSONResponse

from core.image import CleanImage
from core.parser import TokenParser
from utils.exceptions import InvalidImage
from utils.helpers import executor_function


class DetectionAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Detection API"
        self.version = "1.0.0"
        self.description = (
            "An API that detects discord bot tokens in images using tesseract-ocr"
        )
        self.cleaner = CleanImage()
        self.parser = TokenParser()
        self.logger = logger

    @executor_function
    def read_image(self, data_in_bytes: BytesIO) -> str:
        """
        An executor function that reads an image and returns the text found in the image.

        Parameters
        ----------
        data_in_bytes : BytesIO
            The image data in bytes.

        Returns
        -------
        str
            The text found in the image.
        """
        try:
            image = self.cleaner.clean(image_as_bytes=data_in_bytes)
            cleaned_image = self.cleaner.to_pil_image(image)
        except InvalidImage:
            logger.error("Image could not be opened as it is not a valid url.")
            raise fastapi.exceptions.HTTPException(
                status_code=500,
                detail="Image could not be opened due to url being invalid.",
            )

        text = pytesseract.image_to_string(cleaned_image, lang="eng")
        return text

    async def search_token_in_image(self, image_url: str) -> JSONResponse:
        """
        Searches for discord bot tokens in an image.

        Parameters
        ----------
        image_url : str
            The url of the image to search for tokens in, must be a valid url.

        Returns
        -------
        JSONResponse
            A dictionary is returned containing data of the token if found or an error message if not.

        """

        try:
            async with aiohttp.request("GET", image_url) as response:
                if response.status != 200:
                    logger.error(
                        f"Image could not be downloaded. Status: {response.status}"
                    )
                    raise fastapi.exceptions.HTTPException(
                        status_code=410, detail="Image resource not found."
                    )
                image_data = self.read_image(
                    data_in_bytes=BytesIO(await response.read())
                )

                data_from_image = await self.parser.validate_token(image_data)
                json_data = data_from_image.jsonify()
                return JSONResponse(
                    content=json_data, status_code=200, media_type="application/json"
                )
        except aiohttp.InvalidURL:
            self.logger.error("Image url is not a valid url.")
            raise fastapi.exceptions.HTTPException(status_code=400, detail="Invalid Image URL provided.")

    async def search_token_in_text(self, text: typing.AnyStr) -> JSONResponse:
        """
        Searches for discord bot tokens in a text.

        Parameters
        ----------
        text : str
            The text to search for tokens in.

        Returns
        -------
        JSONResponse
            A dictionary is returned containing data of the token if found or an error message if not.

        """
        json_data = (await self.parser.validate_token(text)).jsonify()
        return JSONResponse(
            content=json_data, status_code=200, media_type="application/json"
        )
