from django.dispatch import Signal

pre_send = Signal()
post_send = Signal()
on_exception = Signal()
