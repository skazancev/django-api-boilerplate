from django.urls import reverse


def get_admin_url_for_obj(model, pk):
    return reverse(f'admin:{model._meta.app_label}_{model._meta.model_name}_change', args=(pk,))
