from main.settings.common.env import env, BASE_DIR


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = str(BASE_DIR.path('static'))

MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = str(BASE_DIR.path('media'))
