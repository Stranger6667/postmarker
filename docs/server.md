# Server

Examples use the `postmark` client from [Usage](usage.md).

The Server API is available via the `server` manager:

```python
>>> server = postmark.server.get()
>>> server.edit(TrackOpens=True)
```
