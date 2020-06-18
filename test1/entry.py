import aiohttp
from aiohttp import web
from app import app_init

application = app_init.create_app()

if __name__ == '__main__':
    aiohttp.web.run_app(application)
