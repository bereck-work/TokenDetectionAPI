from io import BytesIO

import aiohttp
import fastapi
import pytesseract
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger

from core.parser import TokenParser
from core.reader import CleanImage
from utils.exceptions import InvalidImage
from utils.helpers import Config, executor_function

__all__ = ("DetectionAPI",)


class DetectionAPI(FastAPI):
    """
    This class subclasses the :class:`fastapi.FastAPI` class with its own methods and attributes.
    """
    def __init__(self):
        self.cleaner = CleanImage()
        self.parser = TokenParser()
        self.config = Config()
        self.logger = logger

        super().__init__(
            title="Token Detection API",
            version="1.0.1",
            description="An API developed to detect discord bot tokens using Tesseract OCR engine in a given image. "
            "Built using FastAPI framework.",
            debug=self.config.fastapi_debug_mode,
        )

    @executor_function
    def read_image(self, data: BytesIO) -> str:
        """
        An executor function that reads an image and returns the text found in the image.

        Parameters:
            data (BytesIO): The parameter takes an image as a BytesIO object, that needs to be read.

        Returns:
            (str): The text found in the image.
        """
        try:
            image = self.cleaner.clean(image=data)
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
        |coroutine|
        This method validates and downloads the image from the provided url, if the url is valid and an image is found,
        it calls :class:`core.parser.TokenParser.validate_token` to parse the image for tokens,
        if found, it returns the token and various other information about it in :class:`JSONResponse` object.

        Parameters:
            image_url (str): The url of the image to search for tokens in, must be a valid url containing an image.

        Returns:
        (JSONResponse): :class:A `JSONResponse` object is returned containing the token and
                       various other information about it as a dict, which fastapi will render as a json object.
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
                image_data = await self.read_image(
                    data=BytesIO(await response.read())
                )

                data_from_image = await self.parser.validate_token(
                    image_data, data_parsed_from_type="image"
                )
                json_data = data_from_image.jsonify()
                return JSONResponse(
                    content=json_data, status_code=200, media_type="application/json"
                )
        except aiohttp.InvalidURL:
            self.logger.error("Image url is not a valid url.")
            raise fastapi.exceptions.HTTPException(
                status_code=400, detail="Invalid Image URL provided."
            )

    async def search_token_in_text(self, text: str) -> JSONResponse:
        """
        |coroutine|
        This method calls :meth:`TokenParser.validate_token` to parse the text for tokens,
        if found, it returns the token and various other information about it in :class:`JSONResponse` object.

        Parameters:
            text (str): This parameter takes a text as a string, that needs to be parsed for tokens.

        Returns:
            (JSONResponse): A :class:`JSONResponse` object is returned containing data of the token as a
                        dict which fastapi will render as a json object.
        """
        json_data = (
            await self.parser.validate_token(text, data_parsed_from_type="text")
        ).jsonify()
        return JSONResponse(
            content=json_data, status_code=200, media_type="application/json"
        )

    async def ocr(self, url: str) -> JSONResponse:
        """
        |coroutine|
        This method downloads an image from url, and then uses :func:`read_image` to read the image and
        returns a json response containing the text from the image that was extracted from the function
        :func:`read_image`.

        Parameters:
            url (str): This parameter takes the url of the image that needs to be processed.

        Returns:

        (JSONResponse): A `fastapi.responses.JSONResponse` object is returned containing the text
                        that was read from the image as a dict which fastapi will render as a json object.

        Raises:
            (fastapi.exceptions.HTTPException): If the image could not be downloaded, or the url is not a valid url.
        """
        try:
            async with aiohttp.request("GET", url) as response:
                if response.status != 200:
                    self.logger.error(
                        f"Image could not be downloaded. Status: {response.status}"
                    )
                    raise fastapi.exceptions.HTTPException(
                        status_code=410, detail="Image resource not found."
                    )
                data_from_image = await self.read_image(
                    data_in_bytes=BytesIO(await response.read())
                )

                json_data = {
                    "url": url,
                    "unfiltered_text": data_from_image,
                    "filtered_text": data_from_image.replace("\n", " ")
                    .replace("\f", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\v", ""),
                }
                return JSONResponse(
                    status_code=200, content=json_data, media_type="application/json"
                )
        except aiohttp.InvalidURL:
            self.logger.error("Image url is not a valid url.")
            raise fastapi.exceptions.HTTPException(
                status_code=400, detail="Invalid Image URL provided."
            )
