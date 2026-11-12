# Servers

Examples use the `postmark` client from [Usage](usage.md).

The Servers API manages all servers of the account. It is available via the `servers` manager and needs the account token:

```python
>>> servers = postmark.servers.all(name='Production')
>>> server = postmark.servers.create('Staging', Color='Purple')
>>> server.edit(Name='Staging 2', TrackOpens=True)
>>> server.delete()
'Server Staging 2 removed.'
```

Deleting servers is not enabled for all Postmark accounts; Postmark support can enable it.

For the server of the current server token, see [Server](server.md).
