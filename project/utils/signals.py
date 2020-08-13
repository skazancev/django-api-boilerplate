from django.dispatch import Signal

post_save_queryset = Signal(providing_args=['sender', 'created', 'queryset', 'update_fields'])
