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
from utils.helpers import executor_function, Config


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
        self.config = Config()
        self.logger = logger
        self.debug = self.config.fastapi_debug_mode

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
           A `fastapi.responses.JSONResponse` object
            is returned containing the token and various other information about it
            as a dict, which fastapi will render as a json object.
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
                    data_in_bytes=BytesIO(await response.read())
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
            A `fastapi.responses.JSONResponse` object
            is returned containing data of the token as a dict which fastapi will render as a json object.
        """
        json_data = (
            await self.parser.validate_token(text, data_parsed_from_type="text")
        ).jsonify()
        return JSONResponse(
            content=json_data, status_code=200, media_type="application/json"
        )

    async def ocr(self, url: str) -> JSONResponse:
        """
        An endpoint that searches for discord bot tokens in an image.

        Parameters
        ----------
        url : str
            The url of the image that needs to be processed.

        Returns
        -------
        JSONResponse
            A `fastapi.responses.JSONResponse` object
            is returned containing the text that was read from the image as a dict
             which fastapi will render as a json object.
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
