import aioredis
from fastapi import Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from src.app import DetectionAPI
from utils.helpers import ImageRequest, TextRequest, Token, OCRData

app = DetectionAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    """
    This method is called when the server starts up, it initializes a redis connection.
    """
    redis = await aioredis.from_url(
        url=app.config.redis_address,
        db=app.config.redis_db,
        username=app.config.redis_username,
        password=app.config.redis_password,
        port=app.config.redis_port,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis)


@app.on_event("shutdown")
async def shutdown():
    """
    This method is called when the server shuts down.
    """
    await FastAPILimiter.close()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Reads the root of the server.

    Returns
    -------
    HTMLResponse
        The root of the server.
    """
    return HTMLResponse(
        content=open("static/index.html", "r").read(),
        media_type="text/html",
    )


@app.get("/game", response_class=HTMLResponse)
async def game():
    """
    This endpoint loads a game. Visit the endpoint for more information.

    Returns
    -------
    HTMLResponse
        The root of the server.
    """
    return HTMLResponse(
        content=open("static/game.html", "r").read(),
        media_type="text/html",
    )


@app.post(
    "/token/image/{url}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
    response_model=Token,
)
async def read_token_from_image(
    image: ImageRequest,
) -> JSONResponse:
    """
    This endpoint reads an image from an url and tries extract the token from it, this uses tesseract-ocr, so it might
    not be accurate all the time.

    Parameters
    ----------
        The url of the image to be read, needs to be a base64 encoded string.

    Returns
    -------
        A json response containing the token extracted from the url of the image, if found, and various
        other information related to the token.
    """

    data = await app.search_token_in_image(image.url)
    return data


@app.post(
    "/token/text/{text}",
    dependencies=[Depends(RateLimiter(times=3, seconds=20))],
    response_model=Token,
)
async def read_token_from_text(
    data: TextRequest,
) -> JSONResponse:
    """
    This endpoint reads a text and tries extract a token from it, if found, it will return the token and various
    other information related to the token.

    Parameters
    ----------
        The text that needs to be read.

    Returns
    -------
        A json response containing the token extracted from text, if found, and various
        other information related to the token.
    """
    response = await app.search_token_in_text(data.content)
    return response


@app.post(
    "/ocr/text/{text}",
    dependencies=[Depends(RateLimiter(times=3, seconds=20))],
    response_model=OCRData,
)
async def OCR_endpoint(
    data: ImageRequest,
) -> JSONResponse:
    """
    This enpoint takes an url of an image and tries to extract the text from it. The extracted text will be not
    100% accurate. It uses tesseract-ocr, so it might not be accurate all the time.

    Parameters
    ----------
        The url of image from which the text needs to be extracted.

    Returns
    -------
        A json response containing the text extracted from the image and url of the image.
    """
    response = await app.ocr(data.url)
    return response
