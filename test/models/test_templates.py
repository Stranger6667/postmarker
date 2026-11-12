from unittest.mock import call

import pytest

from postmarker.core import USER_AGENT
from postmarker.models.templates import Template

pytestmark = pytest.mark.vcr


def test_model_repr(template):
    assert str(template) == "Template: Test (983381)"


def test_model_default(template):
    assert isinstance(template, Template)


def test_model_get(template):
    instance = template.get()
    assert isinstance(instance, Template)


def test_model_edit(template):
    assert template.edit(Name="Test") == {
        "Active": True,
        "Name": "Test",
        "TemplateId": 983381,
    }


def test_manager_edit(postmark):
    assert postmark.templates.edit(983381, Name="Test1") == {
        "Active": True,
        "Name": "Test1",
        "TemplateId": 983381,
    }


def test_manager_all(postmark):
    response = postmark.templates.all()
    assert len(response) == 1
    assert isinstance(response[0], Template)


def test_manager_create(postmark):
    template = postmark.templates.create(Name="TestX", Subject="TestSubj", TextBody="Test content")
    assert isinstance(template, Template)
    assert template.Name == "TestX"
    assert template.delete() == "Template 1003802 removed."


def test_manager_validate(postmark):
    response = postmark.templates.validate(Subject="Test", TextBody="Test")
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
        timeout=None,
    )


LAYOUT_HTML = "<html><body>{{{ @content }}}</body></html>"


def test_layouts_create(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {
        "TemplateId": 5678,
        "Name": "Default Layout",
        "Active": True,
        "Alias": "my-layout",
        "TemplateType": "Layout",
        "LayoutTemplate": None,
    }
    layout = postmark_client.templates.create(
        Name="Default Layout",
        HtmlBody=LAYOUT_HTML,
        TextBody="{{{ @content }}}",
        Alias="my-layout",
        TemplateType="Layout",
    )
    # No `Subject` or `LayoutTemplate` keys: Postmark rejects them for layouts
    assert postmark_request.call_args == sent(
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
    assert isinstance(layout, Template)
    assert layout.TemplateType == "Layout"


def test_layouts_create_positional_with_layout(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {
        "TemplateId": 1234,
        "Name": "Onboarding Email",
        "Active": True,
        "Alias": "onboarding-v1",
        "TemplateType": "Standard",
        "LayoutTemplate": "my-layout",
    }
    template = postmark_client.templates.create(
        "Onboarding Email",
        "Hello from {{company.name}}!",
        None,
        "Hello, {{name}}!",
        "onboarding-v1",
        LayoutTemplate="my-layout",
    )
    assert postmark_request.call_args == sent(
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


def test_layouts_edit_clears_layout(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {
        "TemplateId": 1234,
        "Name": "Onboarding Email",
        "Active": True,
        "Alias": "onboarding-v1",
        "LayoutTemplate": None,
    }
    response = postmark_client.templates.edit("onboarding-v1", LayoutTemplate="")
    # An empty string clears the layout; unset fields stay unchanged
    assert postmark_request.call_args == sent("PUT", "/templates/onboarding-v1", json={"LayoutTemplate": ""})
    assert response == postmark_request.return_value.json.return_value


def test_layouts_all_filters(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {
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
    templates = postmark_client.templates.all(TemplateType="Standard", LayoutTemplate="my-layout")
    assert postmark_request.call_args == sent(
        "GET",
        "/templates",
        params={"Count": 100, "Offset": 0, "TemplateType": "Standard", "LayoutTemplate": "my-layout"},
    )
    assert [str(template) for template in templates] == ["Template: Password Recovery Email (1234)"]


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
def test_layouts_validate(postmark_client, postmark_request, kwargs, body):
    postmark_request.return_value.json.return_value = {"AllContentIsValid": True}
    assert postmark_client.templates.validate(**kwargs) == {"AllContentIsValid": True}
    assert postmark_request.call_args == sent("POST", "/templates/validate", json=body)


def test_layouts_push(postmark_client, postmark_request):
    postmark_request.return_value.json.return_value = {
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
    response = postmark_client.templates.push(SourceServerID=997287, DestinationServerID=997285, PerformChanges=False)
    assert postmark_request.call_args == sent(
        "PUT",
        "/templates/push",
        json={"SourceServerID": 997287, "DestinationServerID": 997285, "PerformChanges": False},
        token=("X-Postmark-Account-Token", "ACCOUNT_TOKEN"),
    )
    assert response == postmark_request.return_value.json.return_value
