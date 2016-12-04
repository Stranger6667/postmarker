# coding: utf-8
from postmarker.models.domains import Domain


CASSETTE_NAME = 'domains'


class TestModel:

    def test_get(self, domain):
        assert isinstance(domain, Domain)

    def test_str(self, domain):
        assert str(domain) == 'Domain: example.com (64054)'


class TestManager:

    def test_all(self, postmark):
        domains = postmark.domains.all(count=2)
        assert len(domains) == 2
        assert all(isinstance(domain, Domain) for domain in domains)
