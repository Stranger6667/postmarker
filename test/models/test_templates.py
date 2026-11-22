from unittest.mock import call

import pytest

from postmarker.core import USER_AGENT
from postmarker.models.templates import Template

from ..conftest import aw, twin

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


@pytest.fixture
async def template(client):
    return await aw(client.templates.get(983381))


async def test_model_repr(template, flavor):
    assert str(template) == f"{twin(Template, flavor).__name__}: Test (983381)"


async def test_model_default(flavor, template):
    assert isinstance(template, twin(Template, flavor))


async def test_model_get(flavor, template):
    instance = await aw(template.get())
    assert isinstance(instance, twin(Template, flavor))


async def test_model_edit(template):
    assert await aw(template.edit(Name="Test")) == {
        "Active": True,
        "Name": "Test",
        "TemplateId": 983381,
    }


async def test_manager_edit(client):
    assert await aw(client.templates.edit(983381, Name="Test1")) == {
        "Active": True,
        "Name": "Test1",
        "TemplateId": 983381,
    }


async def test_manager_all(client, flavor):
    response = await aw(client.templates.all())
    assert len(response) == 1
    assert isinstance(response[0], twin(Template, flavor))


async def test_manager_create(client, flavor):
    template = await aw(client.templates.create(Name="TestX", Subject="TestSubj", TextBody="Test content"))
    assert isinstance(template, twin(Template, flavor))
    assert template.Name == "TestX"
    assert await aw(template.delete()) == "Template 1003802 removed."


async def test_manager_validate(client):
    response = await aw(client.templates.validate(Subject="Test", TextBody="Test"))
    assert response == {
        "AllContentIsValid": True,
        "HtmlBody": None,
        "Subject": {
            "ContentIsValid": True,
            "RenderedContent": "Test",
            "ValidationErrors": [],
        },
        "SuggestedTemplateModel": {},
        "TextBody": {
            "ContentIsValid": True,
            "RenderedContent": "Test",
            "ValidationErrors": [],
        },
    }


def sent(method, endpoint, json=None, params=None, token=("X-Postmark-Server-Token", "SERVER_TOKEN")):
    header, value = token
    return call(
        method,
        f"https://api.postmarkapp.com{endpoint}",
        json=json,
        params={} if params is None else params,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT, header: value},
        timeout=30,
    )


LAYOUT_HTML = "<html><body>{{{ @content }}}</body></html>"


async def test_layouts_create(client, flavor, api_request):
    api_request.return_value.json.return_value = {
        "TemplateId": 5678,
        "Name": "Default Layout",
        "Active": True,
        "Alias": "my-layout",
        "TemplateType": "Layout",
        "LayoutTemplate": None,
    }
    layout = await aw(
        client.templates.create(
            Name="Default Layout",
            HtmlBody=LAYOUT_HTML,
            TextBody="{{{ @content }}}",
            Alias="my-layout",
            TemplateType="Layout",
        )
    )
    # No `Subject` or `LayoutTemplate` keys: Postmark rejects them for layouts
    assert api_request.call_args == sent(
        "POST",
        "/templates",
        json={
            "Name": "Default Layout",
            "HtmlBody": LAYOUT_HTML,
            "TextBody": "{{{ @content }}}",
            "Alias": "my-layout",
            "TemplateType": "Layout",
        },
    )
    assert isinstance(layout, twin(Template, flavor))
    assert layout.TemplateType == "Layout"


async def test_layouts_create_positional_with_layout(client, api_request):
    api_request.return_value.json.return_value = {
        "TemplateId": 1234,
        "Name": "Onboarding Email",
        "Active": True,
        "Alias": "onboarding-v1",
        "TemplateType": "Standard",
        "LayoutTemplate": "my-layout",
    }
    template = await aw(
        client.templates.create(
            "Onboarding Email",
            "Hello from {{company.name}}!",
            None,
            "Hello, {{name}}!",
            "onboarding-v1",
            LayoutTemplate="my-layout",
        )
    )
    assert api_request.call_args == sent(
        "POST",
        "/templates",
        json={
            "Name": "Onboarding Email",
            "Subject": "Hello from {{company.name}}!",
            "TextBody": "Hello, {{name}}!",
            "Alias": "onboarding-v1",
            "LayoutTemplate": "my-layout",
        },
    )
    assert template.LayoutTemplate == "my-layout"


async def test_layouts_edit_clears_layout(client, api_request):
    api_request.return_value.json.return_value = {
        "TemplateId": 1234,
        "Name": "Onboarding Email",
        "Active": True,
        "Alias": "onboarding-v1",
        "LayoutTemplate": None,
    }
    response = await aw(client.templates.edit("onboarding-v1", LayoutTemplate=""))
    # An empty string clears the layout; unset fields stay unchanged
    assert api_request.call_args == sent("PUT", "/templates/onboarding-v1", json={"LayoutTemplate": ""})
    assert response == api_request.return_value.json.return_value


async def test_layouts_all_filters(client, api_request, flavor):
    api_request.return_value.json.return_value = {
        "TotalCount": 1,
        "Templates": [
            {
                "Active": True,
                "TemplateId": 1234,
                "Name": "Password Recovery Email",
                "Alias": "password-recovery",
                "TemplateType": "Standard",
                "LayoutTemplate": "my-layout",
            }
        ],
    }
    templates = await aw(client.templates.all(TemplateType="Standard", LayoutTemplate="my-layout"))
    assert api_request.call_args == sent(
        "GET",
        "/templates",
        params={"Count": 100, "Offset": 0, "TemplateType": "Standard", "LayoutTemplate": "my-layout"},
    )
    assert [str(template) for template in templates] == [
        f"{twin(Template, flavor).__name__}: Password Recovery Email (1234)"
    ]


@pytest.mark.parametrize(
    "kwargs, body",
    (
        (
            {"HtmlBody": LAYOUT_HTML, "TemplateType": "Layout"},
            {"HtmlBody": LAYOUT_HTML, "InlineCssForHtmlTestRender": True, "TemplateType": "Layout"},
        ),
        (
            {"Subject": "Hi", "TextBody": "Hello", "LayoutTemplate": "my-layout"},
            {
                "Subject": "Hi",
                "TextBody": "Hello",
                "InlineCssForHtmlTestRender": True,
                "LayoutTemplate": "my-layout",
            },
        ),
    ),
    ids=("layout", "standard-with-layout"),
)
async def test_layouts_validate(client, api_request, kwargs, body):
    api_request.return_value.json.return_value = {"AllContentIsValid": True}
    assert await aw(client.templates.validate(**kwargs)) == {"AllContentIsValid": True}
    assert api_request.call_args == sent("POST", "/templates/validate", json=body)


async def test_layouts_push(client, api_request):
    api_request.return_value.json.return_value = {
        "TotalCount": 1,
        "Templates": [
            {
                "Action": "Create",
                "TemplateId": 7270,
                "Alias": "comment-notification",
                "Name": "Comment notification",
                "TemplateType": "Standard",
            }
        ],
    }
    response = await aw(client.templates.push(SourceServerID=997287, DestinationServerID=997285, PerformChanges=False))
    assert api_request.call_args == sent(
        "PUT",
        "/templates/push",
        json={"SourceServerID": 997287, "DestinationServerID": 997285, "PerformChanges": False},
        token=("X-Postmark-Account-Token", "ACCOUNT_TOKEN"),
    )
    assert response == api_request.return_value.json.return_value
