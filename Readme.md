# Welcome

This is an API written in python that uses FastAPI. It is a simple API that can detect discord tokens in Images.


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
As we have included a `pyproject.toml` file, it will install the dependencies automatically.

## Bot Configuration
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
Preview mode is special mode that will open a ngrok tunnel that portforwards the localhost address and port, so that the world can see it. 
Although, please don't use this in production.

You will need ngrok installed in your system and ngrok needs to be properly configured.


## Note
This project is still in development, and the API is not stable / accurate yet. You can run the API in preview mode if you want to test it.
The Readme will be updated as the project progresses.

Docker support will be added in the future.

## Credits
Well, this project is entirely free and Open Source, if you want, you can certainly use it in your own projects.
If you like this project, you can add a GitHub star to show your appreciation, and you can credit me in your project.
Thanks :)
Have a nice day!