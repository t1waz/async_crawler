import os


MODELS = (
    'links.models',
)

URL_WORKER_SESSION_TIMEOUT = 30

MAIN_PIPELINE = [
    'workers.UrlWorker',
    'workers.LinkDataWorker',
]

DATABASE_CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.getenv('POSTGRES_HOST'),
                'port': os.getenv('POSTGRES_PORT'),
                'user': os.getenv('POSTGRES_USER'),
                'password': os.getenv('POSTGRES_PASSWORD'),
                'database': os.getenv('POSTGRES_NAME'),
            }
        },
    },
    'apps': {
        'models': {
            'models': MODELS,
        }
    }
}


