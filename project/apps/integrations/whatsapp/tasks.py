from typing import List

from apps.integrations.whatsapp.models import WhatsAppTemplate, WhatsAppTemplateVersion, WhatsAppPhoneNumber
from celeryapp.app import app
from clients.facebook import WhatsAppClient
from utils.core import Dict


@app.task
def update_whatsapp_templates():
    client = WhatsAppClient()
    templates: List[Dict] = client.retrieve_all_paging_data(client.get_message_templates, limit=100)
    existing_templates = dict(WhatsAppTemplate.objects.values_list('name', 'id'))
    for item in templates:
        template_id = existing_templates.get(item.name) or WhatsAppTemplate.objects.create(name=item.name).id
        if item.name not in existing_templates:
            existing_templates[item.name] = template_id

        WhatsAppTemplateVersion.objects.update_or_create(
            template_id=template_id,
            vendor_id=item.id,
            defaults=dict(
                is_active=True,
                language=item.language,
                category=item.category,
                status=item.status,
                components=item.components,
            )
        )

    WhatsAppTemplateVersion.objects.exclude(
        vendor_id__in=[template.id for template in templates]
    ).update(is_active=False)


@app.task
def update_whatsapp_phone_numbers():
    client = WhatsAppClient()
    phone_numbers = client.retrieve_all_paging_data(client.get_phone_numbers, limit=100)
    for number in phone_numbers:
        WhatsAppPhoneNumber.objects.update_or_create(
            vendor_id=number.id,
            defaults=dict(
                name=number.verified_name,
                display=number.display_phone_number,
            )
        )
