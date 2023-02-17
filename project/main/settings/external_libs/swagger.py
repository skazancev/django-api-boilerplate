from main.settings.common.env import env


SHOW_SWAGGER = env.bool('SHOW_SWAGGER', default=True)
SWAGGER_SETTINGS = {
    'LOGOUT_URL': 'admin:logout',
    'LOGIN_URL': 'admin:login',
    'JSON_EDITOR': True,
    # 'SECURITY_DEFINITIONS': {
    #     'api_key': {
    #         'type': 'apiKey',
    #         'in': 'header',
    #         'name': 'Authorization'
    #     }
    # }
}
