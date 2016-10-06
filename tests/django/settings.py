# coding: utf-8

SECRET_KEY = 'foo'

EMAIL_BACKEND = 'postmarker.django.backend.EmailBackend'
POSTMARK = {
    'TOKEN': '<YOUR POSTMARK SERVER TOKEN>'
}
