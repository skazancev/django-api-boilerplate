import pytest
from _pytest.fixtures import SubRequest
from rest_framework.test import APIClient


def fixture_with_params(*argnames):
    def getfixture_wrapper(func):
        def fixture(request: SubRequest):
            def wrapper(*args, **kwargs):
                return func(*[request.getfixturevalue(argname) for argname in argnames], *args, **kwargs)
            return wrapper
        return fixture

    return getfixture_wrapper


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def set_test_settings(settings, tmpdir):
    settings.TEST = True
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.MEDIA_ROOT = tmpdir.strpath
    settings.DEBUG = True
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True


@pytest.fixture(scope='session')
def django_db_use_migrations():
    return False


@pytest.fixture
def ac():
    return APIClient()
