from main.settings.common.env import env


FACEBOOK_VALIDATION_MARKER = env('FACEBOOK_VALIDATION_MARKER', default='marker')
FACEBOOK_SERVER_USER_TOKEN = env('FACEBOOK_SERVER_USER_TOKEN', default='')
WHATSAPP_DEFAULT_LANGUAGE = env('WHATSAPP_DEFAULT_LANGUAGE', default='en_US')
