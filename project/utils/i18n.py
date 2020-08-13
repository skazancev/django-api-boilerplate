import builtins

from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy as __


def builtins_install():
    builtins.__dict__['_'] = _
    builtins.__dict__['__'] = __


__all__ = ['builtins_install']
