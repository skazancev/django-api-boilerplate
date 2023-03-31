from main.settings.common.env import env, BASE_DIR, PROJECT_DIR


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = str(BASE_DIR.path('static'))

STATICFILES_DIRS = [
    str(PROJECT_DIR.path('static'))
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = str(BASE_DIR.path('media'))

# private media
PRIVATE_MEDIA_URL = env('PRIVATE_MEDIA_URL', default='/media/private/')
PRIVATE_MEDIA_ROOT = str(BASE_DIR.path('media/private'))
