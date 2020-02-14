import settings as settings
from urls import routes
from pathlib import Path
from uvicorn.main import run
from dotenv import load_dotenv
from starlette.applications import Starlette
from tortoise.contrib.starlette import register_tortoise


load_dotenv(dotenv_path=Path('.') / '.env')

app = Starlette(debug=True, 
                routes=routes)


register_tortoise(app=app,
                  config=settings.DATABASE_CONFIG, 
                  generate_schemas=True)


if __name__ == "__main__":
    run('main:app', 
        port=settings.PORT,
        reload=settings.RELOAD, 
        workers=settings.WORKERS)
