# Sender signatures

Examples use the `postmark` client from [Usage](usage.md).

The Sender signatures API is available via the `senders` manager:

```python
>>> sender_signature = postmark.senders.get(128462)
>>> sender_signature.delete()
```

`ConfirmationPersonalNote` adds context for the recipient of the confirmation email, up to 400 characters:

```python
>>> postmark.senders.create(
    'john.doe@example.com',
    'John Doe',
    ConfirmationPersonalNote='Postmark sends email for our app.',
)
```
