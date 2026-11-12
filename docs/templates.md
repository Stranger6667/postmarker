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

## Layouts

A layout holds the HTML and text shared by standard templates: CSS, header,
footer. Create one with `TemplateType="Layout"` and put the content
placeholder `{{{ @content }}}` where the template goes. Layouts have no
`Subject`:

```python
postmark.templates.create(
    Name="Default Layout",
    Alias="my-layout",
    HtmlBody="<html><body>{{{ @content }}}</body></html>",
    TextBody="{{{ @content }}}",
    TemplateType="Layout",
)
```

A standard template uses the layout via its alias:

```python
postmark.templates.create(
    Name="Welcome",
    Alias="welcome",
    Subject="Welcome, {{name}}!",
    HtmlBody="<p>Hello, {{name}}!</p>",
    LayoutTemplate="my-layout",
)
```

`edit` switches the layout, and an empty string removes it. The template type
can't change after creation:

```python
postmark.templates.edit("welcome", LayoutTemplate="")
```

Filter templates by type (`All`, `Standard` or `Layout`) or by layout alias:

```python
layouts = postmark.templates.all(TemplateType="Layout")
using_layout = postmark.templates.all(LayoutTemplate="my-layout")
```

Validate a layout, or a standard template rendered inside a layout:

```python
postmark.templates.validate(
    HtmlBody="<html><body>{{{ @content }}}</body></html>",
    TemplateType="Layout",
)
postmark.templates.validate(
    Subject="Welcome, {{name}}!",
    HtmlBody="<p>Hello, {{name}}!</p>",
    LayoutTemplate="my-layout",
)
```

## Push to another server

`push` copies templates with changes from one server to another: it updates
templates the destination already has and creates the rest. It needs the
account token:

```python
>>> postmark = PostmarkClient(
...     server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN"
... )
>>> postmark.templates.push(
...     SourceServerID=997287, DestinationServerID=997285, PerformChanges=False
... )
{
    'TotalCount': 1,
    'Templates': [
        {
            'Action': 'Create',
            'TemplateId': 7270,
            'Alias': 'comment-notification',
            'Name': 'Comment notification',
            'TemplateType': 'Standard'
        }
    ]
}
```

`PerformChanges=False` is a dry run: it lists the changes without making them.
Pass `PerformChanges=True` to push.
