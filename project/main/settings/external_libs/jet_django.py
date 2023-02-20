from main.settings.common.env import env


# JET_PROJECT = 'boilerplate'
# JET_TOKEN = 'ebbf5920-cca8-4923-8e11-6190af68a67d'

JET_PROJECT = env('JET_PROJECT', default='')
JET_TOKEN = env('JET_TOKEN', default='')
