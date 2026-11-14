import pytest

from postmarker.exceptions import ClientError
from postmarker.models.domains import Domain

from ..conftest import aw, twin

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


async def get_domain(client):
    return await aw(client.domains.get(64054))


async def test_model_get(client, flavor):
    domain = await get_domain(client)
    assert isinstance(domain, twin(Domain, flavor))
    assert await aw(domain.get())


async def test_model_str(client, flavor):
    assert str(await get_domain(client)) == f"{twin(Domain, flavor).__name__}: example.com (64054)"


async def test_manager_all(client, flavor):
    domains = await aw(client.domains.all(count=2))
    assert len(domains) == 2
    assert all(isinstance(domain, twin(Domain, flavor)) for domain in domains)


async def test_manager_domain_methods(client):
    domain = await aw(client.domains.create("newsuperdomain.name"))
    await aw(domain.edit(ReturnPathDomain="pm.newsuperdomain.name"))
    assert domain.ReturnPathDomain == "pm.newsuperdomain.name"
    assert await aw(domain.verifyspf()) == {
        "SPFHost": "newsuperdomain.name",
        "SPFTextValue": "v=spf1 a mx include:spf.mtasv.net ~all",
        "SPFVerified": True,
    }
    assert await aw(domain.verifydkim()) == {
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
    assert await aw(domain.verifyreturnpath()) == {
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
        await aw(domain.rotatedkim())
    assert str(exc.value) == "[505] This DKIM is already being renewed."
    assert await aw(domain.delete()) == "Domain newsuperdomain.name removed."
