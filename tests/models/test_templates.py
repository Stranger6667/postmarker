# coding: utf-8
from postmarker.models.templates import Template


CASSETTE_NAME = "templates"


class TestModel:
    def test_repr(self, template):
        assert str(template) == "Template: Test (983381)"

    def test_default(self, template):
        assert isinstance(template, Template)

    def test_get(self, template):
        instance = template.get()
        assert isinstance(instance, Template)

    def test_edit(self, template):
        assert template.edit(Name="Test") == {"Active": True, "Name": "Test", "TemplateId": 983381}


class TestManager:
    def test_edit(self, postmark):
        assert postmark.templates.edit(983381, Name="Test1") == {"Active": True, "Name": "Test1", "TemplateId": 983381}

    def test_all(self, postmark):
        response = postmark.templates.all()
        assert len(response) == 1
        assert isinstance(response[0], Template)

    def test_create(self, postmark):
        template = postmark.templates.create(Name="TestX", Subject="TestSubj", TextBody="Test content")
        assert isinstance(template, Template)
        assert template.Name == "TestX"
        assert template.delete() == "Template 1003802 removed."

    def test_validate(self, postmark):
        response = postmark.templates.validate(Subject="Test", TextBody="Test")
        assert response == {
            "AllContentIsValid": True,
            "HtmlBody": None,
            "Subject": {"ContentIsValid": True, "RenderedContent": "Test", "ValidationErrors": []},
            "SuggestedTemplateModel": {},
            "TextBody": {"ContentIsValid": True, "RenderedContent": "Test", "ValidationErrors": []},
        }
