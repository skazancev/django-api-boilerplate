from split_settings.tools import optional, include

include(
    'common/__init__.py',
    'external_libs/*.py',
    'project/*.py',
    optional('local_settings.py'),
)
