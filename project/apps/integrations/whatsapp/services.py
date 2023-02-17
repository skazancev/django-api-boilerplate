from project.apps.facebook.whatsapp.models import WhatsAppPhoneNumber


def get_default_phone_number() -> WhatsAppPhoneNumber:
    if phone_number := WhatsAppPhoneNumber.objects.filter(default=True).first():
        return phone_number
    raise ValueError('Default phone number for whatsapp does not exists.')
