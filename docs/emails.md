# Emails

Examples use the `postmark` client from [Usage](usage.md).

## Basic

Sending emails is super easy! Here is the simplest case:

```python
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
{'ErrorCode': 0,
 'Message': 'OK',
 'MessageID': 'fbff8f29-1742-48ee-93c2-f881c7049402',
 'SubmittedAt': '2016-10-05T06:51:08.9753663-04:00',
 'To': 'receiver@example.com'}
```

Or send `MIMEText`/`MIMEMultipart` instances:

```python
>>> message = MIMEText('Text')
>>> message['From'] = 'sender@example.com'
>>> message['To'] = 'receiver@example.com'
>>> postmark.emails.send(message=message)
```

To specify multiple recipients (or `Cc` / `Bcc`) you could pass values as a list or string with comma separated values:

```python
>>> postmark.emails.send(
    From='sender@example.com',
    # The same as To='first@example.com, second@example.com'
    To=['first@example.com', 'second@example.com'],
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
```

Headers could be specified as a dict:

```python
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Headers={'X-Accept-Language': 'en-us, en'},
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
```

Attachments could be specified as a list of items in the following forms:

```python
# Dictionary
>>> msg_1 = {
    "Name": "readme.txt",
    "Content": "dGVzdCBjb250ZW50",
    "ContentType": "text/plain",
}
# Tuple
>>> msg_2 = ("readme.txt", "dGVzdCBjb250ZW50", "text/plain")
# MIMEBase instance
>>> msg_3 = MIMEBase('text', 'plain')
>>> msg_3.set_payload('dGVzdCBjb250ZW50')
>>> msg_3.add_header('Content-Disposition', 'attachment', filename='readme.txt')
# File path string. Content type will be detected automatically
>>> msg_4 = '/home/user/readme.txt'
```

Note! Content should be encoded as Base64 string. Then pass the attachments to `send()`:

```python
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.',
    Attachments=[msg_1, msg_2, msg_3, msg_4]
)
```

Postmarker also supports inline images. Here are the possible usage options:

```python
>>> tuple_image = ('image', 'content', 'image/png', 'cid:image@example.com')
>>> mime = MIMEImage('test content', 'png', name='image1.png')
>>> mime.add_header('Content-ID', '<image1@example.com>')
>>> mime_inline = MIMEImage('test content', 'png', name='image3.png')
>>> mime_inline.add_header('Content-ID', '<image3@example.com>')
>>> mime_inline.add_header(
    'Content-Disposition', 'inline', filename='image3.png'
)
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.',
    Attachments=[tuple_image, mime, mime_inline]
)
```

To send email in a batch there is `send_batch()` method.

```python
>>> postmark.emails.send_batch(
    {
        'From': 'sender@example.com',
        'To': 'receiver@example.com',
        'Subject': 'Postmark test',
        'HtmlBody': '<strong>Hello</strong> dear Postmark user.',
    },
    {
        'From': 'sender2@example.com',
        'To': 'receiver2@example.com',
        'Subject': 'Postmark test 2',
        'HtmlBody': '<strong>Hello</strong> dear Postmark user.',
    }
)
```

You can pass either `Email`/`MIMEText`/`MIMEMultipart` instances or dictionaries. Additionally, you may pass extra keywords to use with every email in a batch.

Emails are separate arguments. To send a list, unpack it:

```python
>>> emails = [email_1, email_2]
>>> postmark.emails.send_batch(*emails)
```

The batch size is not limited, but if the batch has more than 500 emails, then before sending, it will be split into chunks of 500 emails.

Postmark provides an interface to send emails created with a template. Example of usage with Postmarker:

```python
>>> postmark.emails.send_with_template(
    TemplateId=123,
    TemplateModel={'username': 'Test'}
    From='sender@example.com',
    To='receiver@example.com',
)
```

Attachments and headers work in the same way as in basic email sending.

## CSS inlining

Some email clients drop `<style>` blocks. Postmarker can move that CSS into `style` attributes with [css-inline](https://github.com/Stranger6667/css-inline):

```
pip install 'postmarker[css-inline]'
```

```python
>>> postmark = PostmarkClient(server_token='API_TOKEN', inline_css=True)
>>> postmark.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<html><head><style>h1 { color: red }</style></head><body><h1>Hello</h1></body></html>'
)
```

Postmark receives `<h1 style="color: red;">Hello</h1>`. Inlining applies to `send`, `send_batch`, `Email` objects and Python email instances. Postmark inlines template emails itself, see `InlineCss` in `send_with_template`.

Stylesheets from `<link>` tags are not loaded. To change it or other options, pass a `CSSInliner` instance:

```python
>>> import css_inline
>>> postmark = PostmarkClient(
    server_token='API_TOKEN',
    inline_css=css_inline.CSSInliner(keep_style_tags=True),
)
```

With `load_remote_stylesheets=True`, your server fetches every `<link>` URL in the email HTML, so enable it only for HTML you control.

## Advanced

To get more flexibility it is possible to use `Email` objects. `EmailManager` uses them internally to send emails. To instantiate one:

```python
>>> email = postmark.emails.Email(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    HtmlBody='<strong>Hello</strong> dear Postmark user.'
)
```

Then send it:

```python
>>> email.send()
```

To specify headers:

```python
>>> email['X-Accept-Language'] = 'en-us, en'
```

Also it is possible to remove the header:

```python
>>> del email['X-Accept-Language']
```

To add an attachment to an email there is `attach()` method.

```python
>>> email.attach(msg_1)
```

To attach multiple attachments, pass them all to `attach()`:

```python
>>> email.attach(msg_1, msg_2, msg_3)
```

Also it is possible to attach binary data:

```python
>>> content = b'test content'
>>> email.attach_binary(content=content, filename='readme.txt')
```

Batches are available via the `EmailBatch()` constructor.

```python
>>> batch = postmark.emails.EmailBatch(email)
>>> len(batch)
1
>>> batch.send()
```

For now, batches expose a very limited interface - only `send()` method and length information via the `len` function.

Template batches are available via the `EmailTemplateBatch()` constructor.

```python
>>> batch = postmark.emails.EmailTemplateBatch(template)
>>> len(batch)
1
>>> batch.send()
```
