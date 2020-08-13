import environ

env = environ.Env()
PROJECT_DIR = environ.Path(__file__) - 1

env.read_env(str(PROJECT_DIR.path('config.env')))

broker_api = env.str('FLOWER_BROKER_API', default='http://guest:guest@rabbit:15672/api/')
basic_auth = env.str('FLOWER_BASIC_AUTH', default=['user:secretps'])
