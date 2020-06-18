from . import routes
from .app_logic import find_articles_main


@routes.get('/task')
async def upload(request):
    query = request.rel_url.query
    category = query['category']
    period = query['period']
    phrase = query['phrase']

    await find_articles_main(category.lower(), period.lower(), phrase.lower())
