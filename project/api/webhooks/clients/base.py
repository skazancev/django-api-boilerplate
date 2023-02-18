from django.db import transaction

from apps.webhooks.models import WebhookData


class BaseClient:
    def __init__(self, webhook):
        self.webhook: WebhookData = webhook
        self.content = webhook.data

    def find_method_to_process_webhook(self, action=None):
        method = action or self.process_type()
        if method is not None:
            try:
                func = getattr(self, method)
            except AttributeError:
                return None
            else:
                return func

    @transaction.atomic()
    def process(self, action=None):
        if handler_method := self.find_method_to_process_webhook(action):
            result = handler_method()
            self.webhook.is_processed = True
            self.webhook.save(update_fields=['is_processed'])
            return result

    def process_type(self) -> str:
        """
        Gets method name for processing given webhook content
        @return: string
        """
        raise NotImplementedError
