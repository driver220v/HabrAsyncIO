from aiohttp import web


from .app_init import create_app

habr_intitial = 'https://habr.com/ru/'
routes = web.RouteTableDef()

from . import app_routes