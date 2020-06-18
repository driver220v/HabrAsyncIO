from aiohttp import web


async def create_app():
    """Create an application."""
    app = web.Application()

    from .app_routes import routes

    app.add_routes(routes)
    return app

