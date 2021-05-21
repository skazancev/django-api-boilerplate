from typing import List

from django.conf import settings
from sendgrid import sendgrid

from apps.communication.models import SendgridTemplate, Template, UserFlowAction, CommunicationHistory

from celeryapp.app import app


@app.task
def update_sendgrid_templates():
    sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
    data = sg.client.templates.get(query_params={'generations': 'dynamic'}).to_dict
    updated = []
    for template in data['templates']:
        versions = template['versions']
        defaults = {
            'name': template['name'],
            'modified': template['updated_at'],
            'is_active': False,
        }
        if version := [i for i in versions if i['active'] == 1]:
            version = version[0]
            defaults.update({
                'active_version_id': version['id'],
                'subject': version['subject'],
                'preview_url': f'https://{version["thumbnail_url"]}' if 'thumbnail_url' in version else None,
                'is_active': True,
            })
        template, created = SendgridTemplate.objects.update_or_create(template_id=template['id'], defaults=defaults)
        updated.append(template.template_id)

    SendgridTemplate.objects.exclude(template_id__in=updated).update(is_active=False)
    Template.objects.active().filter(sendgrid_template__is_active=False).update(is_active=False)


@app.task
def send_user_flow_action(action_id: int):
    from apps.communication.services import user_flow_action as user_flow_action_service

    user_flow_action = UserFlowAction.objects.get(id=action_id)
    user_flow_action_service.send(user_flow_action)


@app.task
def send_communications(communications: List[int]):
    from apps.communication.services import communications as communications_service
    queryset = CommunicationHistory.objects.filter(id__in=communications)
    communications_service.send_multiple(queryset)
