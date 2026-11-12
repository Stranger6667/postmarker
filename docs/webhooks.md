# Webhooks

Examples use the `postmark` client from [Usage](usage.md).

## Inbound

### Basic

The webhook data could automatically decoded from JSON with `postmark.messages.inbound.InboundMessage`.

```python
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> inbound = postmark.messages.inbound.InboundMessage(data)
```

It works in the same way as a regular `InboundMessage`.

## Delivery

For delivery webhook there is a wrapper - `Delivery` with the regular model interface as in any other model (e.g. `InboundMessage`):

```python
>>> from postmarker.models.emails import Delivery
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> hook = Delivery.from_json(data)
>>> hook.Recipient
john@example.com
```

## Open

Opens could be processed by `postmark.messages.outbound.opens.Open`:

```python
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> open = postmark.messages.outbound.opens.Open(data)
```

## Bounce

For bounce webhook processing there is `Bounce` constructor in `bounces` manager. It constructs new `Bounce` instance from given JSON string.

```python
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> bounce = postmark.bounces.Bounce(data)
>>> bounce.activate()
'OK'
```

Another way to parse a bounce - use `Bounce.from_json` method:

```python
>>> from postmarker.models.bounces import Bounce
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> bounce = Bounce.from_json(data)
```

But in this case, there is no possibility to work with the bounce - only parsed data will be available.

## Spam complaint

For spam complaint webhook there is `SpamComplaint` constructor in `bounces` manager. A spam complaint is a `Bounce` that can't be activated, so `message` and `dump` work as for a bounce:

```python
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> complaint = postmark.bounces.SpamComplaint(data)
>>> complaint
<Spam complaint from john@example.com>
>>> complaint.Description
'The subscriber explicitly marked this message as spam.'
```

## Subscription change

Subscription changes could be processed by `postmark.suppressions.SubscriptionChange`. `SuppressSending` is `True` when an address is suppressed and `False` when it is reactivated:

```python
>>> with open('/path/to/raw_content.json') as fd:
        data = fd.read()
>>> change = postmark.suppressions.SubscriptionChange(data)
>>> change
<Subscription change for john@example.com>
>>> change.SuppressSending, change.SuppressionReason
(True, 'HardBounce')
```

`change.message` fetches the related message. `MessageID` is `None` for reactivations and for manual suppressions with `Origin` of `Customer` or `Admin`, so there is no message to fetch.
