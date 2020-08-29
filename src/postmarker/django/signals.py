from django.dispatch import Signal

pre_send = Signal(providing_args=["messages"])
post_send = Signal(providing_args=["messages", "response"])
on_exception = Signal(providing_args=["raw_messages", "exception"])
