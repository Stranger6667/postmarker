# Message Streams

Examples use the `postmark` client from [Usage](usage.md).

The Message Streams API is available via the `message_streams` manager.
It uses the server token.

List streams, optionally filtered by type and including archived ones:

```python
>>> postmark.message_streams.all()
[<MessageStream: outbound>, <MessageStream: inbound>, ...]
>>> postmark.message_streams.all(
...     MessageStreamType="Broadcasts", IncludeArchivedStreams=True
... )
[<MessageStream: broadcasts>]
```

Get a stream by its ID:

```python
>>> stream = postmark.message_streams.get("broadcasts")
>>> stream.Name
'Broadcast Stream'
```

Create a stream. `MessageStreamType` is `Transactional` or `Broadcasts`:

```python
>>> stream = postmark.message_streams.create(
...     ID="transactional-dev",
...     Name="My Dev Transactional Stream",
...     MessageStreamType="Transactional",
...     Description="This is my second transactional stream",
... )
```

Edit a stream; fields you leave out stay unchanged:

```python
>>> stream.edit(Name="Updated Dev Stream")
>>> stream.edit(
...     SubscriptionManagementConfiguration={
...         "UnsubscribeHandlingType": "Postmark"
...     }
... )
```

Archive a stream. Postmark deletes it after `ExpectedPurgeDate` (45 days):

```python
>>> stream.archive()
{
    'ID': 'transactional-dev',
    'ServerID': 123457,
    'ExpectedPurgeDate': '2020-08-30T12:30:00.00-04:00'
}
```

Restore an archived stream before then:

```python
>>> stream.unarchive()
<MessageStream: transactional-dev>
```

The manager offers the same operations by stream ID. Its `edit` and
`unarchive` return a new `MessageStream`:

```python
postmark.message_streams.edit("transactional-dev", Name="New name")
postmark.message_streams.archive("transactional-dev")
postmark.message_streams.unarchive("transactional-dev")
```
