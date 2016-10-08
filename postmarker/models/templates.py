# coding: utf-8
from .base import Model, ModelManager


class Template(Model):

    def __str__(self):
        return '%s: %s (%s)' % (self.__class__.__name__, self._data.get('Name'), self._data.get('TemplateId'))

    def get(self):
        new_instance = self._manager.get(self.TemplateId)
        self._data = new_instance._data
        return self

    def edit(self, **kwargs):
        return self._manager.edit(self.TemplateId, **kwargs)

    def delete(self):
        return self._manager.delete(self.TemplateId)


class TemplateManager(ModelManager):
    name = 'templates'
    model = Template

    def get(self, id):
        response = self._call('GET', '/templates/%s' % id)
        return self._init_instance(response.json())

    def create(self, Name, Subject, HtmlBody=None, TextBody=None):
        """
        Creates a template.

        :param Name: Name of template
        :param Subject: The content to use for the Subject when this template is used to send email.
        :param HtmlBody: The content to use for the HtmlBody when this template is used to send email.
        :param TextBody: The content to use for the HtmlBody when this template is used to send email.
        :return:
        """
        assert TextBody or HtmlBody, 'Provide either email TextBody or HtmlBody or both'
        data = {
            'Name': Name,
            'Subject': Subject,
            'HtmlBody': HtmlBody,
            'TextBody': TextBody,
        }
        return self._call('POST', '/templates', data=data)

    def edit(self, id, Name=None, Subject=None, HtmlBody=None, TextBody=None):
        data = {
            'Name': Name,
            'Subject': Subject,
            'HtmlBody': HtmlBody,
            'TextBody': TextBody,
        }
        return self._call('PUT', '/templates/%s' % id, data=data)

    def all(self, Count=100, Offset=0):
        response = self._call('GET', '/templates', Count=Count, Offset=Offset)
        return [self._init_instance(template) for template in response.json()['Templates']]

    def delete(self, id):
        response = self._call('DELETE', '/templates/%s' % id).json()
        return response['Message']

    def validate(self, Subject, HtmlBody, TextBody, TestRenderModel, InlineCssForHtmlTestRender=True):
        data = {
            'Subject': Subject,
            'HtmlBody': HtmlBody,
            'TextBody': TextBody,
            'TestRenderModel': TestRenderModel,
            'InlineCssForHtmlTestRender': InlineCssForHtmlTestRender,
        }
        return self._call('POST', '/templates/validate', data=data).json()
