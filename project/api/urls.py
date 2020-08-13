from django.urls import path, include

app_name = 'api'
apps = [
    'utils',
    'accounts',
    'emails',
]

urlpatterns = [
    path(f'{app}/', include(f'api.{app}.urls'))
    for app in apps
]
