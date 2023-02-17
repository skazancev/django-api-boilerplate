from main.settings.common.env import env
from main.settings.common.apps import INSTALLED_APPS
from main.settings.common.middleware import MIDDLEWARE

# django-debug-toolbar
# ------------------------------------------------------------------------------
DEBUG_TOOLBAR = env.bool('DEBUG_TOOLBAR', default=True)
if DEBUG_TOOLBAR:
    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        DEBUG_TOOLBAR = False

    else:
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': 'main.settings.show_toolbar',
            'SHOW_COLLAPSED': True,
        }

        def show_toolbar(request):
            # Включает DjDT для DEBUG=False
            return True
