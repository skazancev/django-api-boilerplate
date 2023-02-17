import collections
import json

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from utils.json import JSONEncoder


def cut_dict(dict_, maxdepth, replaced_with=None):
    """Cuts the dictionary at the specified depth.

    If maxdepth is n, then only n levels of keys are kept.
    """
    if not isinstance(dict_, dict):
        return dict_

    queue = collections.deque([(dict_, 0)])

    # invariant: every entry in the queue is a dictionary
    while queue:
        parent, depth = queue.popleft()
        for key, child in parent.items():
            if isinstance(child, dict):
                if depth == maxdepth - 1:
                    parent[key] = replaced_with
                else:
                    queue.append((child, depth + 1))


def pretty_typeform(content, cut=False):
    formatter = HtmlFormatter(style='default')
    try:
        if isinstance(content, str):
            content = json.loads(content)
    except json.JSONDecodeError:
        pass
    else:
        if cut:
            cut_dict(content, 1)
        content = json.dumps(content, indent=2, ensure_ascii=False, cls=JSONEncoder)
        response = highlight(content, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)
