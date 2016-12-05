# coding: utf-8
import pytest

from postmarker.exceptions import ClientError
from postmarker.models.domains import Domain


CASSETTE_NAME = 'domains'


class TestModel:

    def test_get(self, domain):
        assert isinstance(domain, Domain)
        assert domain.get()

    def test_str(self, domain):
        assert str(domain) == 'Domain: example.com (64054)'


class TestManager:

    def test_all(self, postmark):
        domains = postmark.domains.all(count=2)
        assert len(domains) == 2
        assert all(isinstance(domain, Domain) for domain in domains)

    def test_domain_methods(self, postmark):
        domain = postmark.domains.create('newsuperdomain.name')
        domain.edit(ReturnPathDomain='pm.newsuperdomain.name')
        assert domain.ReturnPathDomain == 'pm.newsuperdomain.name'
        assert domain.verifyspf() == {
            'SPFHost': 'newsuperdomain.name',
            'SPFTextValue': 'v=spf1 a mx include:spf.mtasv.net ~all',
            'SPFVerified': False
        }
        with pytest.raises(ClientError) as exc:
            assert domain.rotatedkim()
        assert str(exc.value) == '[505] This DKIM is already being renewed.'
        assert domain.delete() == 'Domain newsuperdomain.name removed.'
