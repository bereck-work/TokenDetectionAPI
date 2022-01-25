# Welcome

This repository hosts the source code of a simple API built using [FastAPI](https://fastapi.tiangolo.com) framework.

## Installation
There are currently two ways to install:

Use [pip package manager](https://pip.pypa.io/en/stable/) to install the libraries from ``requirements.txt`` file.

```bash
pip install -r requirements.txt
```

If you have [Poetry package manager](https://python-poetry.org/) installed, you can install the dependencies using 
the following command.

```bash
poetry install
```
As we have included a `pyproject.toml` file, poetry will automatically install the dependencies from the file.

# How does this API work?
This API is based on [Tesseract OCR library](https://), an open source OCR engine that can extract text / text data from images.

This API works in two main steps:
1.) Image processing
The image is extracted from the url in bytes and then the image is `cleaned` using [pillow](https://github.com/python-pillow/Pillow). The cleaning process is done by grayscaling, removing noise, and then applying some masks to make the image cleaner and better for Tesseract to parse the image with more accuracy.
2.) OCR
The image is processed by Tesseract OCR library. The library processes the image that was parsed, and then extracts the text from the image.

3.) Token detection and validation

The text is parsed and the API uses a regex to find token like strings in the text, if a match is found, the token goes through a validation process.

The validation process checks that the token was extracted is a valid token, if it is a valid token, the API returns the token and information about the token.

Visit [Tesseract documentation](https://github.com/tesseract-ocr/tesseract/wiki) for more information about Tesseract and how it works.

# Token Validation
<img src="./static/images/token.png" width=450px></img>

The above image shows the details about different components of a discord bot token. 
A token is composed of 3 components:

1.) User ID - The user ID of the bot that the token belongs to.

2.) Time Stamp - The time stamp epoch used for tokens.

3.)Hmac - Hmac is a cryptographic component that is used to verify the token by Discord.

All the above components are encoded in base64 encoding and is seperated by a `.` character.

The API uses a regex to find the token in the text, if a match is found, the token goes through a validation process.
The validation process is composed of the following steps:

1.) First the user ID is extracted from the token, and it is decoded from base64. If the API fails to decode the User ID, the token is invalid, as the base64 encoded string is not valid.

2.) The time stamp is extracted from the token, and it is decoded from base64 to an integer, if the API fails to decode the time stamp, the token is invalid.
If the timestamp is valid, is the added to a token epoch (special epoch used for tokens) and the sum of the timestamp and the token epoch is compared to Discord's epoch.
If the sum is greater than the Discord epoch, the token is valid, otherwise it is invalid.

3.) The hmac is extracted from the token, and it is decoded from base64. If the API fails to decode the hmac, the token is invalid.
If the hmac is valid, the API checks unique characters in hmac, if the hmac is unique, it has more than 3 unique characters, and the hmac is valid, otherwise it is invalid.

Thanks [arl](https://github.com/onerandomusername/secrets-pre-commit-hook) for the regex used to find the token.

# Installing Tesseract
Tesseract can be installed on linux using the following command:

```bash
    sudo apt-get install tesseract-ocr
    sudo apt-get install libtesseract-dev
```
Pretty simple, right?, cuz linux!

# Endpoints
There are currently three **main** endpoints:
1.) /token/image/url - This endpoint will detect a discord token in an image, and return the token if it is valid.

2.) /token/text/string - This endpoint will detect a discord token in a string, and return the token if it is valid.

3.) /orc/text/string - This endpoint will read an image from the provided url and return the text that was detected.

All these endpoints are POST requests, and you need to pass the data to its respective request body.
Visit /docs for detailed information on these endpoints and the API itself.

## API Configuration
You can configure the app by using the file called ``config.yml`` in the ``config`` directory.
You need to pass the host, port for uvicorn to run the server.
```yaml
Settings:
  host: "127.0.0.1"
  port: 7000
  preview: "true"  # Preview mode opens a ngrok tunnel that portforwards the localhost address and port, so that the world can see it. Although, please don't use this in production

Redis:
  address: "Your Redis Address"
  port: 0000  #  Your Redis Port
  database: 0  #  Your Redis Database
  username: "..."  #  Your Redis Username, if ACL is enabled. Required.
  password: "..." #  Your Redis Password, if ACL is enabled.  Required.
  
```
## Preview Mode
It is a special mode that will open a ngrok tunnel that will portforward the localhost address and port, so it can be accessed from anywhere.
You will need to have ngrok installed on your machine, with ngrok properly setup.
Visit [ngrok.com](https://ngrok.io/) to install ngrok and for more information on how to set up ngrok.


## Note
This project is still in development, and the API is not stable / accurate yet. You can run the API in preview mode if you want to test it.

This `Readme` will be updated as the project progresses.

This API has only been tested on linux (Pop!_OS) so it is not guaranteed to work on other operating systems.

Docker support will be added in the future, which will eliminate the above note.

## Credits
Well, this project is entirely free and Open Source, if you want, you can certainly use it in your own projects.
If you like this project, you can add a GitHub star to show your appreciation, and you can credit me in your project.
Thanks :)
Have a nice day!
