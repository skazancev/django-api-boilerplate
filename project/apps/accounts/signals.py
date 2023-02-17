from django.dispatch import Signal

user_logged_in = Signal()

user_signed_up = Signal()

password_set = Signal()
password_changed = Signal()
password_reset = Signal()

email_confirmed = Signal()
email_confirmation_sent = Signal()
