# Sender signatures

Examples use the `postmark` client from [Usage](usage.md).

The Sender signatures API is available via the `senders` manager:

```python
>>> sender_signature = postmark.senders.get(128462)
>>> sender_signature.delete()
```
