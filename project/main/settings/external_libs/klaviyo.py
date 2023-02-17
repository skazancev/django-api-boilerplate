from main.settings.common.env import env


KLAVIYO_PUBLIC_TOKEN = env('KLAVIYO_PRIVATE_TOKEN', default='')
KLAVIYO_PRIVATE_TOKEN = env('KLAVIYO_PRIVATE_TOKEN', default='')
KLAVIYO_ENABLED = env('KLAVIYO_ENABLED', default=True)
