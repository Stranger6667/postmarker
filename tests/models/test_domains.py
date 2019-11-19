# coding: utf-8
import pytest

from postmarker.exceptions import ClientError
from postmarker.models.domains import Domain


CASSETTE_NAME = "domains"


class TestModel:
    def test_get(self, domain):
        assert isinstance(domain, Domain)
        assert domain.get()

    def test_str(self, domain):
        assert str(domain) == "Domain: example.com (64054)"


class TestManager:
    def test_all(self, postmark):
        domains = postmark.domains.all(count=2)
        assert len(domains) == 2
        assert all(isinstance(domain, Domain) for domain in domains)

    def test_domain_methods(self, postmark):
        domain = postmark.domains.create("newsuperdomain.name")
        domain.edit(ReturnPathDomain="pm.newsuperdomain.name")
        assert domain.ReturnPathDomain == "pm.newsuperdomain.name"
        assert domain.verifyspf() == {
            "SPFHost": "newsuperdomain.name",
            "SPFTextValue": "v=spf1 a mx include:spf.mtasv.net ~all",
            "SPFVerified": True,
        }
        assert domain.verifydkim() == {
            "Name": "newsuperdomain.name",
            "SPFVerified": True,
            "SPFHost": "newsuperdomain.name",
            "SPFTextValue": "v=spf1 a mx include:spf.mtasv.net ~all",
            "DKIMVerified": False,
            "WeakDKIM": False,
            "DKIMHost": "",
            "DKIMTextValue": "",
            "DKIMPendingHost": "20161205155228pm._domainkey.newsuperdomain.name",
            "DKIMPendingTextValue": "k=rsa;p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCybzS6rWqf9HTgnydKCL+wOkmYMisbvQIULMYEV6Rqtz1to71RFEru2d3dPI003GF4Lfra81hbAtrgp9Zk1v7BabzmhKIACTinNrLNaEK3EOz1Ro3Czt/qS0LhSuiK8dhWP8miz4Zc/VyzqnkhWHbX8YuxEWfvGLEjPv6ytjl25QIDAQAB",
            "DKIMRevokedHost": "",
            "DKIMRevokedTextValue": "",
            "SafeToRemoveRevokedKeyFromDNS": False,
            "DKIMUpdateStatus": "Pending",
            "ReturnPathDomain": "newsuperdomain.name",
            "ReturnPathDomainVerified": False,
            "ReturnPathDomainCNAMEValue": "pm.mtasv.net",
            "ID": 386143,
        }
        assert domain.verifyreturnpath() == {
            "Name": "newsuperdomain.name",
            "SPFVerified": True,
            "SPFHost": "newsuperdomain.name",
            "SPFTextValue": "v=spf1 a mx include:spf.mtasv.net ~all",
            "DKIMVerified": False,
            "WeakDKIM": False,
            "DKIMHost": "",
            "DKIMTextValue": "",
            "DKIMPendingHost": "20161205155228pm._domainkey.newsuperdomain.name",
            "DKIMPendingTextValue": "k=rsa;p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCybzS6rWqf9HTgnydKCL+wOkmYMisbvQIULMYEV6Rqtz1to71RFEru2d3dPI003GF4Lfra81hbAtrgp9Zk1v7BabzmhKIACTinNrLNaEK3EOz1Ro3Czt/qS0LhSuiK8dhWP8miz4Zc/VyzqnkhWHbX8YuxEWfvGLEjPv6ytjl25QIDAQAB",
            "DKIMRevokedHost": "",
            "DKIMRevokedTextValue": "",
            "SafeToRemoveRevokedKeyFromDNS": False,
            "DKIMUpdateStatus": "Pending",
            "ReturnPathDomain": "newsuperdomain.name",
            "ReturnPathDomainVerified": False,
            "ReturnPathDomainCNAMEValue": "pm.mtasv.net",
            "ID": 386143,
        }
        with pytest.raises(ClientError) as exc:
            assert domain.rotatedkim()
        assert str(exc.value) == "[505] This DKIM is already being renewed."
        assert domain.delete() == "Domain newsuperdomain.name removed."
