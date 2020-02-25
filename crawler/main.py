import settings
from urls import routes
from starlette.applications import Starlette
from utils.helpers import register_pipeline
from tortoise.contrib.starlette import register_tortoise


app = Starlette(debug=True, 
                routes=routes)

register_tortoise(app,
                  config=settings.DATABASE_CONFIG, 
                  generate_schemas=True)

queue = register_pipeline(app,
                          services=settings.MAIN_PIPELINE)

app.state.queue = queue
