import logging
from functools import cached_property

import slack
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


class SlackClient:
    FILE_EXTENSIONS = ['txt', 'html']

    @cached_property
    def client(self):
        return slack.WebClient(settings.SLACK_TOKEN)

    def render_template(self, template_name, **context):
        for extension in self.FILE_EXTENSIONS:
            try:
                return render_to_string(f'slack/texts/{template_name}.{extension}', context)
            except TemplateDoesNotExist:
                pass

        return template_name

    def send_msg(self, recipient, msg, **kwargs):
        if not settings.SLACK_ENABLED:
            return
        self.client.chat_postMessage(channel=recipient, text=mark_safe(self.render_template(msg)), **kwargs)
