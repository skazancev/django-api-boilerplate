import html

from django.core.exceptions import ValidationError
from django.db import models
from django.template import Context, Template as DjangoTemplate
from django_better_admin_arrayfield.models.fields import ArrayField
from simple_history.models import HistoricalRecords

from apps.bases.models import BaseModel
from utils.fields import ActiveField


class Template(BaseModel):
    class Types(models.TextChoices):
        mail = 'mail', _('Письмо')
        sms = 'sms', _('SMS')

    is_active = ActiveField()
    subject = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField()
    sendgrid_template = models.ForeignKey('SendgridTemplate', models.SET_NULL, null=True, blank=True, limit_choices_to={
        'is_active': True,
    })
    type = models.CharField(choices=Types.choices, max_length=20, default=Types.mail)
    bcc_emails = ArrayField(base_field=models.CharField(max_length=40), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = _('Шаблоны')

    def __str__(self):
        return f'({self.get_type_display()}) {self.get_subject()}' \
               f'{f" (Sendgrid: {self.sendgrid_template.name})" if self.sendgrid_template_id else ""}'

    def clean(self):
        super().clean()
        if not self.sendgrid_template_id and not (self.subject and self.body):
            raise ValidationError('Subject and body must be filled if sendgrid template is not used.')

    def format_subject(self, context):
        t = DjangoTemplate(html.unescape(self.get_subject()))
        return t.render(Context(context))

    def format_body(self, context={}):
        template = DjangoTemplate(self.body)
        return template.render(Context(context))

    def get_subject(self):
        return self.subject or (self.sendgrid_template.subject if self.sendgrid_template_id else '-')
    get_subject.short_description = 'Subject'


class SendgridTemplate(BaseModel):
    template_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, editable=False)
    active_version_id = models.CharField(max_length=255, null=True, editable=False)
    subject = models.CharField(max_length=255, null=True, editable=False)
    preview_url = models.URLField(null=True, editable=False)
    is_active = ActiveField()

    def __str__(self):
        return f'{self.name} — {self.subject}{"(no active)" if not self.is_active else ""}'
