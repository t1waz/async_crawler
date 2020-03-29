from starlette.applications import Starlette
from tortoise.contrib.starlette import register_tortoise

import settings
from urls import routes
from utils.pipelines import register_pipeline


app = Starlette(debug=True,
                routes=routes)

register_tortoise(app,
                  config=settings.DATABASE_CONFIG, 
                  generate_schemas=True)

queue = register_pipeline(app,
                          services=settings.MAIN_PIPELINE)

app.state.queue = queue
