# Messages

Examples use the `postmark` client from [Usage](usage.md).

## Inbound messages

The inbound messages API is available via the `messages.inbound` manager:

```python
>>> postmark.messages.inbound.all()
[<InboundMessage: Blocked message from test@example.com>, ...]
```

There is a simple way to access the headers in the `InboundMessage` instance:

```python
>>> inbound['X-Spam-Status']
No
```

Also, you can convert inbound message to MIME instance:

```python
>>> inbound.as_mime()
<email.mime.multipart.MIMEMultipart object at 0x10a232c88>
```

### Attachments

To access the attachments you could use the `Attachments` attribute of the `InboundMessage` which returns a list of attachments.

```python
>>> inbound.Attachments
[<Attachment: test.txt>]
```

The interface is the same - all keys-value pairs in JSON data are attributes of the `Attachment`:

```python
>>> attachment = inbound.Attachments[0]
>>> attachment.Name
test.txt
```

Besides it, you could do the following with attachments:

- Access the decoded content
- Check it length
- Save it locally
- Convert it to MIME instance

```python
>>> len(attachment)
45
>>> attachment.decoded
This is attachment contents, base-64 encoded.
>>> attachment.save('/directory/to/save/')
/directory/to/save/test.txt
>>> attachment.as_mime()
<email.mime.base.MIMEBase at 0x10424b7b8>
```

## Outbound messages

The outbound messages API is available via the `messages.outbound` manager:

```python
>>> postmark.messages.outbound.all()
[<OutboundMessage: Sent message to test@example.com>, ...]
```

## Opens

The opens API handler is located in `messages.outbound.opens` manager.

```python
>>> postmark.messages.outbound.opens.all()
[<Open: Open from test@example.com>, ...]
```

Also, you can access to corresponding `OutboundMessage` instance via `message` property.

```python
>>> open.message
<Sent message to test@example.com>
```
