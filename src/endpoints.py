import aioredis
from fastapi import Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.app import DetectionAPI
from utils.models import ImageRequest, OCRData, TextRequest, Token

app = DetectionAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup() -> None:
    """
    |coroutine|
    This method is triggered when the FastAPI app instance starts up, it is binded to the event named as
    `startup` in the above listener (decorator).
    This function initializes the redis connection.
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
    return


@app.on_event("shutdown")
async def shutdown() -> None:
    """
    |coroutine|

    This method is binded to the shutdown event of the server triggered when the FastAPI app instance shuts down,
    it closes the redis connection.
    """
    await FastAPILimiter.close()
    return


@app.get("/", response_class=HTMLResponse)
async def read_root() -> HTMLResponse:
    """
    This endpoint is the root endpoint of the API.
    """
    return HTMLResponse(
        content=open("static/index.html", "r").read(),
        media_type="text/html",
    )


@app.get("/game", response_class=HTMLResponse)
async def game() -> HTMLResponse:
    """
    This endpoint contains an experimental web based game.
    """
    return HTMLResponse(
        content=open("static/game.html", "r").read(),
        media_type="text/html",
    )


@app.post(
    "/token/image/{url}",
    dependencies=[Depends(RateLimiter(times=1, seconds=30))],
    response_model=Token,
)
async def read_token_from_image(
    image: ImageRequest,
) -> JSONResponse:
    """
    This endpoint reads an image from an url and tries extract the token from it, this uses tesseract-ocr, so it might
    not be accurate all the time.
    This endpoint has a rate limiter, so you can only make 1 request every 30 seconds.
    """

    data = await app.search_token_in_image(image.url)
    return data


@app.post(
    "/token/text/{text}",
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    response_model=Token,
)
async def read_token_from_text(
    data: TextRequest,
) -> JSONResponse:
    """
    This endpoint reads a text and tries extract a token from it, if found, it will return the token and various
    other information related to the token.
    This endpoint has a rate limiter, so you can only make 1 request every 10 seconds.
    """
    response = await app.search_token_in_text(data.content)
    return response


@app.post(
    "/ocr/text/{text}",
    dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    response_model=OCRData,
)
async def OCR_endpoint(data: ImageRequest) -> JSONResponse:
    """
    This enpoint takes an url of an image, validates and downloads the image and returns the text extracted from it in
    :class:`OCRData` response. This endpoint uses Tesseract OCR engine to process the image.
    This endpoint has a rate limiter, so you can only make 1 request every 10 seconds.
    """
    response = await app.ocr(data.url)
    return response
