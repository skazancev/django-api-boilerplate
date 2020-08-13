import html

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.template import Template, Context
from django.template.loader import render_to_string
from django_better_admin_arrayfield.models.fields import ArrayField
from djchoices import DjangoChoices, ChoiceItem
from simple_history.models import HistoricalRecords

from utils.models import BaseModel, DynamicChoiceField


class EmailTemplate(BaseModel):
    class Types(DjangoChoices):
        accounts_password_change = ChoiceItem('accounts_password_change', label=_('Пользователь сменил пароль'))
        accounts_password_reset = ChoiceItem('accounts_password_reset', label=_('Восстановление пароля'))
        accounts_password_set = ChoiceItem('accounts_password_set', label=_('Создание нового пароля'))
        accounts_email_confirm = ChoiceItem('accounts_email_confirm', label=_('Подтверждение адреса эл. почты'))

    type = DynamicChoiceField(method='get_email_types_choices', max_length=50, unique=True, choices=Types.choices)
    subject = models.CharField(max_length=255)
    body = RichTextUploadingField()
    from_addr = models.CharField(max_length=255, blank=True, default=settings.DEFAULT_FROM_EMAIL)
    send_after_hours = models.FloatField(default=0, help_text='Delay before sending mail')

    extra_recipients = ArrayField(base_field=models.CharField(max_length=40), null=True, blank=True)
    cc_emails = ArrayField(base_field=models.CharField(max_length=40), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['type']
        verbose_name = _('Шаблон письма')
        verbose_name_plural = _('Шаблоны писем')

    def str(self):
        return self.type

    def format_subject(self, context):
        t = Template(html.unescape(self.subject))
        return t.render(Context(context))

    def format_body(self, context={}):
        template = Template(self.body)
        ctx = Context(context)

        result_context = {
            'subject': self.subject,
            'body': template.render(ctx),
            'website': context.get('website')
        }

        return render_to_string('emails/base.html', result_context)

    @classmethod
    def get_email_types_choices(cls):
        return cls.Types.choices
