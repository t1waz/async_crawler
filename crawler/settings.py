import os


PORT = 9000

RELOAD = True

WORKERS = 10

TASK_SESSION_TIMEOUT = 3

MODELS = (
    'links.models',
)

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
