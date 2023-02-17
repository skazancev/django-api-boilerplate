from main.settings.common.env import env

# SLACK
SLACK_ENABLED = env.bool('SLACK_ENABLED', default=False)
SLACK_TOKEN = env('SLACK_TOKEN', default='')
