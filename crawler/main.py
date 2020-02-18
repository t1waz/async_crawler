import settings
from urls import routes
from pathlib import Path
from uvicorn.main import run
from dotenv import load_dotenv
from starlette.applications import Starlette
from utils.helpers import register_pipeline
from tortoise.contrib.starlette import register_tortoise


load_dotenv(dotenv_path=Path('..') / '.env')

app = Starlette(debug=True, 
                routes=routes)

register_tortoise(app,
                  config=settings.DATABASE_CONFIG, 
                  generate_schemas=True)

queue = register_pipeline(app,
                          services=settings.MAIN_PIPELINE)

app.state.queue = queue


if __name__ == "__main__":
    run('main:app', **settings.APP_SETTINGS)
