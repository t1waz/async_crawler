import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path('.') / '.env', verbose=True)


APP_SETTINGS = {
    'port': 9000,
    'reload': True,
    'workers': 10
}

MODELS = (
    'links.models',
)

URL_WORKER_SESSION_TIMEOUT = 30

MAIN_PIPELINE = [
    'workers.UrlWorker',
    'workers.LinkDataWorker',
]

DATABASE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
            }
        },
    },
    "apps": {
        "models": {
            "models": MODELS,
        }
    }
}
