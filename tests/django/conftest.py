# coding: utf-8
import pytest


@pytest.fixture(autouse=True)
def outbox(settings):
    """
    It is necessary, because pytest-django uses django.utils.setup_test_environment, where
    EMAIL_BACKEND is set explicitly to 'django.core.mail.backends.locmem.EmailBackend'.
    """
    settings.EMAIL_BACKEND = 'postmarker.django.backend.EmailBackend'
