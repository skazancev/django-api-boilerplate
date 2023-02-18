from .accounts import AccountsViewSet
from .auth import AuthViewSet
from .password import PasswordAuthViewSet
from .magic_link import MagicLinkAuthViewSet


__all__ = [
    'AccountsViewSet',
    'AuthViewSet',
    'PasswordAuthViewSet',
    'MagicLinkAuthViewSet',
]
