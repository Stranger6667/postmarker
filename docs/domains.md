# Domains

Examples use the `postmark` client from [Usage](usage.md).

The Domains API is available via the `domains` manager:

```python
>>> domain = postmark.domains.get(1)
>>> domain.edit(ReturnPathDomain='pmbounces.example.com')
```
