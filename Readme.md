# Welcome

This repository contains the source code of a simple API built using [FastAPI](https://fastapi.tiangolo.com) framework.

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
This API is based on [Tesseract OCR library](https://), an open source OCR engine that can extract text from images.

This API works in `three` main steps:
<dl>

<dt> <strong> 1.) Image processing </strong> </dt>
    <dd> The <strong>image</strong> is extracted from the url in bytes and then the image is cleaned using <a href="https://github.com/python-pillow/Pillow">pillow</a> (A very powerful, reliable and robust image processing library written in C with python bindings). The cleaning process is done by grayscaling, removing noise, and then applying some masks to make the image cleaner and better for Tesseract engine to parse the image with high accuracy. </dd>

<dt> <strong> 2.) OCR </strong> </dt>
    <dd> The cleaned image is then passed to <strong> Tesseract OCR engine </strong>. The engine processes the image, and returns the extracted the text from the image. </dd>

<dt> <strong> 3.) Token detection and validation </strong> </dt>
    <dd> The text is parsed and the API uses a regex to find <strong> token like strings </strong> in the text, if a match is found, the token goes through a validation process.
         The validation process checks that the token was extracted is a valid token, if it is a valid token, the API returns the token and information about the token. </dd>

</dl>

## Token detection and validation
<img src="./static/images/token.png" width=450px></img>

The above image shows the details about different components of a discord bot token.

A token is mainly composed of 3 components:

<ol>

<li> <strong> User ID </strong> - <strong> The user ID of the bot that the token belongs to. </strong> </li>

<li> <strong> Timestamp </strong> - <strong> The unix time when the token was generated. </strong> </li>

<li> <strong> Hmac </strong> - <strong> Hmac is a cryptographic component that Discord authentication uses to verify the token, this isn't very useful to us.</strong> </li>

</ol>

All the above components are encoded in base64 encryption and is seperated by a `.` character.

The API uses a regex to find the token in the text, if a match is found, the token goes through a validation process.

The validation process is composed of the following steps:

<ol>
<li> First the user ID is extracted from the token, and it is decoded from base64. If the API fails to decode the user ID, the user ID is invalid, as the base64 encoded string is not valid. </li>


<li> The time stamp is extracted from the token, and it is decoded from base64 to an integer, if the API fails to decode the timestamp, the timestamp is invalid.
     If the timestamp is valid, it is the added to a token epoch (special epoch used for tokens) and the sum of the timestamp and the token epoch is compared to Discord's epoch.
     If the sum is greater than the Discord epoch, the timestamp is valid, otherwise it is invalid. </li>


<li> The hmac is extracted from the token, and it is decoded from base64. If the API fails to decode the hmac, the token is invalid.
     If the hmac is valid, the API checks unique characters in hmac, if the hmac is unique, it has more than 3 unique characters, and the hmac is valid, otherwise it is invalid. </li>
</ol>

If the token passes all the above condition, it is deemed as a valid discord bot token, and the API returns the token and information about the token.
If the token fails any of the above condition, the token is deemed as invalid.

However, this validation process in itself is flawed due to the nature of discord bots, there is no way to know if the token is <strong> valid </strong> or <strong> invalid </strong> without actually running the bot token through Discord API, but that poses a security risk and no one will want that.

If you pass a valid token like string which is actually not valid but just a string that looks like a valid token, it will still be deemed as valid.


# Tesseract
Tesseract is an open source and powerful OCR library developed by **Google** that is used to process images and extract text from them.

Installation of Tesseract is pretty easy on linux, you can install it by running the following command:

```bash
  sudo apt-get install tesseract-ocr
  sudo apt-get install libtesseract-dev
```

The above command will install Tesseract OCR library and the CLI tool.
Tesseract can be directly used by a terminal as Tesseract originally is a CLI based library. After installing tesseract we have to install tesseract language data.

```bash
 sudo apt-get install tesseract-ocr-eng
```
This will install the English language data (tessdata) for Tesseract. You can install other languages by running the following command:


```bash
 sudo apt-get install tesseract-ocr-<language>
```
To know more about Tesseract and how it works, you can visit the following link:
<a href="https://tesseract-ocr.github.io/">Tesseract Documentation</a>


# Endpoints
There are currently three **main** endpoints:

1.) ```/token/image/url``` - `This endpoint will detect a discord token in an image, and return the token if it is valid.`

2.) ```/token/text/string``` - `This endpoint will detect a discord token in a string, and return the token if it is valid.`

3.) ```/ocr/text/string``` - `This endpoint will read an image from the provided url and return the text that was detected.`

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
Visit [ngrok](https://ngrok.io/) to install ngrok and for more information on how to set up ngrok.


## Note
This project is still in development, and the API is not stable / accurate yet. You can run the API in preview mode if you want to test it.

This `Readme` will be updated as the project progresses.

This API has only been tested on linux (Pop!_OS) so it is not guaranteed to work on other operating systems.

Docker support will be added in the future, which will eliminate the above issue.

## Credits
Well, this project is entirely free and Open Source, if you want, you can certainly use it in your own projects.
If you like this project, you can add a GitHub star to show your appreciation, and you can credit me in your project.
Thanks :)
Have a nice day!
