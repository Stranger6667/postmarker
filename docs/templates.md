# Templates

Create the client first ([Usage](usage.md) lists all its options):

```python
>>> from postmarker.core import PostmarkClient
>>> postmark = PostmarkClient(server_token='SERVER_TOKEN')
```

The Templates API is available via the `templates` manager:

```python
>>> template = postmark.templates.get(983381)
>>> template
<Template: Test (983381)>
>>> template.edit(Name='New name')
>>> postmark.templates.all()
[<Template: Test1 (983381)>, <Template: TestX (1003801)>]
```

To send an email based on the template, use send_with_template:

```python
postmark.emails.send_with_template(
    TemplateId=123456,
    TemplateModel={"foo": "bar"},
    From="sender@example.com",
    To="johndoe@example.com",
)
```

Template validation:

```python
>>> postmark.templates.validate(Subject='Test', TextBody='Test')
{
    'AllContentIsValid': True,
    'HtmlBody': None,
    'Subject': {
        'ContentIsValid': True,
        'RenderedContent': 'Test',
        'ValidationErrors': []
    },
    'SuggestedTemplateModel': {},
    'TextBody': {
        'ContentIsValid': True,
        'RenderedContent': 'Test',
        'ValidationErrors': []
    }
}
```
