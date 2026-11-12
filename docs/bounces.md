# Bounces

Information about bounces is available via the `BounceManager`, which is an attribute of `postmark` instance.

```python
>>> postmark.bounces
<BouncesManager>
```

You can get a list of bounces with the `all()` method:

```python
>>> postmark.bounces.all()
[<Bounce: 943247350>, <Bounce: 924829573>]
```

Default number of bounces, which will be returned is 500 to fit in single network request. More than 500 items will be fetching in multiple network requests:

```python
>>> postmark.bounces.all(count=1001)
[<Bounce: 943247350>, <Bounce: 924829573>, ...]
```

Here it will be 3 network requests, single one is limited by 500 items. To load all available data, pass `None` as `count` value. Postmark caps `count` + `offset` at 10,000 for bounces and messages, so filter larger result sets with `fromdate` and `todate`.

Every bounce instance is represented by its ID. You can search be specifying the ID.

```python
>>> bounce = postmark.bounces.get(943247350)
>>> bounce
<Bounce: 943247350>
```

Bounce could be activated.

```python
>>> bounce.activate()
'OK'
```

Or you can get an SMTP dump if it is available.

```python
>>> bounce.dump
'A lot of text'
```

Also, you can access to corresponding `OutboundMessage` instance via `message` property.

```python
>>> bounce.message
<Sent message to test@example.com>
```
