from .add import AddView
from .change import ChangeView
from .changelist import ChangeListView
from .core import (
    IndexView,
    AppIndexView,
    LanguageCatalogView,
    AutoCompleteView,
    SiteContextView,
    AdminLogView,
    AdminAPIRootView,
)
from .csrftoken import CsrfTokenView
from .delete import DeleteView
from .detail import DetailView
from .handle_action import HandleActionView
from .history import HistoryView
from .list import ListView
from .user import (
    UserInformation,
    LoginView,
    LogoutView,
    PasswordChangeView,
)


__all__ = [
    'AddView',
    'ChangeView',
    'ChangeListView',
    'IndexView',
    'AppIndexView',
    'LanguageCatalogView',
    'AutoCompleteView',
    'SiteContextView',
    'AdminLogView',
    'AdminAPIRootView',
    'CsrfTokenView',
    'DeleteView',
    'DetailView',
    'HandleActionView',
    'HistoryView',
    'ListView',
    'UserInformation',
    'LoginView',
    'LogoutView',
    'PasswordChangeView',
]
