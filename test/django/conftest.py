# coding: utf-8
import pytest


@pytest.fixture
def outbox(settings):
    """Configure Django's email backend.

    It is necessary, because pytest-django uses django.utils.setup_test_environment, where
    EMAIL_BACKEND is set explicitly to 'django.core.mail.backends.locmem.EmailBackend'.
    """
    settings.EMAIL_BACKEND = "postmarker.django.EmailBackend"
