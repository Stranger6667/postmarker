# Domains

The Domains API is available via the `domains` manager:

```python
>>> domain = postmark.domains.get(1)
>>> domain.edit(ReturnPathDomain='pmbounces.example.com')
```
