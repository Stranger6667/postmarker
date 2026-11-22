# Async client

`AsyncPostmarkClient` has the same API as `PostmarkClient`. Every method and property that makes a request is a coroutine.
Install the `async` extra, which adds [httpx2](https://github.com/pydantic/httpx2):

```
uv pip install 'postmarker[async]'
```

```python
from postmarker.core import AsyncPostmarkClient

async with AsyncPostmarkClient(server_token="POSTMARK_API_TEST") as postmark:
    await postmark.emails.send(
        From="sender@example.com",
        To="receiver@example.com",
        Subject="Postmark test",
        HtmlBody="<strong>Hello</strong> dear Postmark user.",
    )
```

`async with` closes the connection pool on exit. Without it, call `await postmark.aclose()` when you are done.

## Same API, awaited

Managers, models and their methods keep the sync names and arguments:

```python
bounce = await postmark.bounces.get(723626745)
await bounce.activate()
templates = await postmark.templates.all()
await postmark.emails.send_batch(*messages)
```

Properties that make a request stay properties, so you await them: `await bounce.dump`, `await postmark.status.services`, `await postmark.bounces.deliverystats`.

Each async class has the sync name with an `Async` prefix, in the same module: `AsyncBounce` in `postmarker.models.bounces`, `AsyncEmail` in `postmarker.models.emails`.
Webhook wrappers on the async client return async models, so `await postmark.bounces.Bounce(payload).message` loads the related message.

## Differences from the sync client

- `max_retries` doesn't apply to requests through a proxy from `HTTP_PROXY` / `HTTPS_PROXY`: httpx2 doesn't retry proxy connections.
- Batches accept the async email classes: pass `AsyncEmail` instances, dictionaries or `email.message.Message` instances to `send_batch`.

## Testing

Postmarker ships `postmark_async_request` and `postmark_async_client`, the async versions of [the sync fixtures](testing.md).
`postmark_async_request` records calls in the same shape as `postmark_request`, so a sync test ports by adding `await`:

```python
async def test_welcome_email(postmark_async_request):
    await send_welcome_email("jane@example.com")  # Your code that sends an email
    assert postmark_async_request.call_args.kwargs["json"]["To"] == "jane@example.com"
```

Run async tests with an async test plugin, e.g. [anyio's](https://anyio.readthedocs.io/en/stable/testing.html) or [pytest-asyncio](https://pytest-asyncio.readthedocs.io/).
