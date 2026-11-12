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
        Subject: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Alias: str | None = None,
        TemplateType: str | None = None,
        LayoutTemplate: str | None = None,
    ) -> Template:
        """Creates a template.

        :param Name: Name of template.
        :param Subject: Subject content. Required for standard templates, rejected for layouts.
        :param HtmlBody: HTML body content.
        :param TextBody: Text body content.
        :param Alias: Template alias.
        :param TemplateType: ``Standard`` (default) or ``Layout``.
        :param LayoutTemplate: Alias of the layout for a standard template.
        """
        assert TextBody or HtmlBody, "Provide either email TextBody or HtmlBody or both"
        data = _present(
            {
                "Name": Name,
                "Subject": Subject,
                "HtmlBody": HtmlBody,
                "TextBody": TextBody,
                "Alias": Alias,
                "TemplateType": TemplateType,
                "LayoutTemplate": LayoutTemplate,
            }
        )
        return self._init_instance(self.call("POST", "/templates", data=data))

    def edit(
        self,
        id: int | str,
        Name: str | None = None,
        Subject: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        Alias: str | None = None,
        LayoutTemplate: str | None = None,
    ) -> Any:
        """Edits a template. Unset fields stay unchanged; ``LayoutTemplate=""`` removes the layout."""
        data = _present(
            {
                "Name": Name,
                "Subject": Subject,
                "HtmlBody": HtmlBody,
                "TextBody": TextBody,
                "Alias": Alias,
                "LayoutTemplate": LayoutTemplate,
            }
        )
        return self.call("PUT", f"/templates/{id}", data=data)

    def all(
        self,
        Count: int | None = 100,
        Offset: int = 0,
        TemplateType: str | None = None,
        LayoutTemplate: str | None = None,
    ) -> list[Template]:
        """Returns templates, optionally filtered by ``TemplateType`` (``All``, ``Standard``, ``Layout``) or layout alias."""
        responses = self.call_many(
            "GET",
            "/templates",
            Count=Count,
            Offset=Offset,
            TemplateType=TemplateType,
            LayoutTemplate=LayoutTemplate,
        )
        return self.expand_responses(responses, "Templates")

    def delete(self, id: int | str) -> Any:
        return self.call("DELETE", f"/templates/{id}")["Message"]

    def validate(
        self,
        Subject: str | None = None,
        HtmlBody: str | None = None,
        TextBody: str | None = None,
        TestRenderModel: dict[str, Any] | None = None,
        InlineCssForHtmlTestRender: bool = True,
        TemplateType: str | None = None,
        LayoutTemplate: str | None = None,
    ) -> Any:
        """Validates template content; ``LayoutTemplate`` renders a standard template inside that layout."""
        data = _present(
            {
                "Subject": Subject,
                "HtmlBody": HtmlBody,
                "TextBody": TextBody,
                "TestRenderModel": TestRenderModel,
                "InlineCssForHtmlTestRender": InlineCssForHtmlTestRender,
                "TemplateType": TemplateType,
                "LayoutTemplate": LayoutTemplate,
            }
        )
        return self.call("POST", "/templates/validate", data=data)

    def push(self, SourceServerID: int | str, DestinationServerID: int | str, PerformChanges: bool) -> Any:
        """Copies changed templates to another server. Needs the account token.

        :param PerformChanges: ``False`` for a dry run that only lists the changes.
        """
        data = {
            "SourceServerID": SourceServerID,
            "DestinationServerID": DestinationServerID,
            "PerformChanges": PerformChanges,
        }
        return self.call("PUT", "/templates/push", token_type="account", data=data)


def _present(data: dict[str, Any]) -> dict[str, Any]:
    # Layouts reject `Subject` and `LayoutTemplate`, so unset fields are left out instead of sent as `null`
    return {key: value for key, value in data.items() if value is not None}
