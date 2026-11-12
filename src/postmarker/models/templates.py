from __future__ import annotations

from typing import Any

from .base import Model, ModelManager


class Template(Model):
    def __str__(self) -> str:
        return "{}: {} ({})".format(
            self.__class__.__name__,
            self._data.get("Name"),
            self._data.get("TemplateId"),
        )

    def get(self) -> Template:
        new_instance = self._manager.get(self.TemplateId)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs: Any) -> Any:
        return self._manager.edit(self.TemplateId, **kwargs)

    def delete(self) -> Any:
        return self._manager.delete(self.TemplateId)


class TemplateManager(ModelManager[Template]):
    name = "templates"
    model = Template
    count_key = "Count"
    offset_key = "Offset"

    def get(self, id: int | str) -> Template:
        response = self.call("GET", f"/templates/{id}")
        return self._init_instance(response)

    def create(
        self,
        Name: str,
        Subject: str,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Alias: str | None = None,
    ) -> Template:
        """Creates a template.

        :param Name: Name of template
        :param Subject: The content to use for the Subject when this template is used to send email.
        :param HtmlBody: The content to use for the HtmlBody when this template is used to send email.
        :param TextBody: The content to use for the HtmlBody when this template is used to send email.
        :return:
        """
        assert TextBody or HtmlBody, "Provide either email TextBody or HtmlBody or both"
        data = {
            "Name": Name,
            "Subject": Subject,
            "HtmlBody": HtmlBody,
            "TextBody": TextBody,
            "Alias": Alias,
        }
        return self._init_instance(self.call("POST", "/templates", data=data))

    def edit(
        self,
        id: int | str,
        Name: str | None = None,
        Subject: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Alias: str | None = None,
    ) -> Any:
        data = {
            "Name": Name,
            "Subject": Subject,
            "HtmlBody": HtmlBody,
            "TextBody": TextBody,
            "Alias": Alias,
        }
        return self.call("PUT", f"/templates/{id}", data=data)

    def all(self, Count: int | None = 100, Offset: int = 0) -> list[Template]:
        responses = self.call_many("GET", "/templates", Count=Count, Offset=Offset)
        return self.expand_responses(responses, "Templates")

    def delete(self, id: int | str) -> Any:
        return self.call("DELETE", f"/templates/{id}")["Message"]

    def validate(
        self,
        Subject: str,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        TestRenderModel: dict[str, Any] | None = None,
        InlineCssForHtmlTestRender: bool = True,
    ) -> Any:
        data = {
            "Subject": Subject,
            "HtmlBody": HtmlBody,
            "TextBody": TextBody,
            "TestRenderModel": TestRenderModel,
            "InlineCssForHtmlTestRender": InlineCssForHtmlTestRender,
        }
        return self.call("POST", "/templates/validate", data=data)
