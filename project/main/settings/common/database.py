# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
from main.settings.common.env import env

DATABASES = {
    'default': {
        **env.db('DATABASE_URL', default=''),
        'ATOMIC_REQUESTS': True,
    }
}
