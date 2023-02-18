import environ

from utils.i18n import builtins_install

builtins_install()

PROJECT_DIR = environ.Path(__file__) - 3
BASE_DIR = environ.Path(__file__) - 4

env = environ.Env()

env.read_env(str(PROJECT_DIR.path('config.env')))

ENVIRONMENT = env('ENVIRONMENT', default='development')
