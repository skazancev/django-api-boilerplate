from main.settings.common.env import env


EMAILS_REPEAT_DELAYS = env.json('EMAILS_REPEAT_DELAYS', default=dict())
