import typing
from io import BytesIO

import PIL.ImageEnhance
import numpy as np
from PIL import ImageFilter, ImageOps
from PIL.Image import Image
from loguru import logger

from utils.exceptions import InvalidImage


class CleanImage:
    """
    A class that cleans an image by removing noise, grayscaling and sharpening it.
    """

    def __init__(self):
        self.image_binary = BytesIO

    @classmethod
    def clean(cls, image_as_bytes: BytesIO) -> BytesIO:
        """
        A method that takes an image and returns a cleaned version of it by removing noise and smoothing it.

        Parameters
        ----------
        image_as_bytes : BytesIO
            The image that needs to be cleaned.

        Returns
        -------
        typing.Optional[BytesIO]
            The cleaned image as a BytesIO object, or None if the image could not be cleaned or if the image is None.
        """
        image_binary = BytesIO()

        if isinstance(image_as_bytes, BytesIO):
            try:
                image = PIL.Image.open(image_as_bytes).convert("L")
            except Exception as e:
                logger.error(e)
                raise InvalidImage("The image could not be converted to a PIL image.")

            image = ImageOps.grayscale(image).filter(ImageFilter.UnsharpMask).filter(ImageFilter.DETAIL)
            image = (
                ImageOps.posterize(image, 4)
                .filter(ImageFilter.SMOOTH)
                .filter(ImageFilter.SHARPEN)
            )
            image.save(image_binary, format="PNG")
            image_binary.seek(0)
            return image_binary

        else:
            raise InvalidImage("The image must be a BytesIO object.")

    @staticmethod
    def to_numpy_array(image_as_bytes: BytesIO) -> np.ndarray:
        """
        Returns an image as a numpy array.

        Parameters
        ----------
        image_as_bytes : BytesIO
            The image to be converted to a numpy array.

        Returns
        -------
        numpy.ndarray
            The image as a numpy array.
        """
        image_binary = BytesIO()
        pil_image = PIL.Image.open(image_as_bytes)
        pil_image.save(image_binary, format="PNG")
        image_binary.seek(0)
        return np.frombuffer(image_binary.read(), dtype=np.uint8)

    @staticmethod
    def to_pil_image(image_as_bytes: BytesIO) -> Image:
        """
        Returns an image as a PIL image.

        Parameters
        ----------
        image_as_bytes : BytesIO
            The image to be converted to a PIL image.

        Returns
        -------
        PIL.Image
            The image as a PIL image object.
        """
        try:
            image = PIL.Image.open(image_as_bytes)
            return image
        except Exception as e:
            logger.error(e)
            raise InvalidImage("The image could not be converted to a PIL image.")

    def __repr__(self):
        return f"CleanImage({self})"
