# coding: utf-8
from django.dispatch import Signal


pre_send = Signal(providing_args=['messages'])
post_send = Signal(providing_args=['messages', 'response'])
