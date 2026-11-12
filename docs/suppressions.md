# Suppressions

Examples use the `postmark` client from [Usage](usage.md).

The Suppressions API is available via the `suppressions` manager.
Every method works on the `outbound` transactional stream unless you pass
another `stream_id`.

## List suppressed addresses

```python
>>> postmark.suppressions.all()
[<Suppression: address@wildbit.com>, ...]
>>> suppressions = postmark.suppressions.all(
...     stream_id="broadcast",
...     SuppressionReason="HardBounce",
...     fromdate="2019-12-01",
... )
>>> suppressions[0].as_dict()
{
    'EmailAddress': 'bounce.address@wildbit.com',
    'SuppressionReason': 'HardBounce',
    'Origin': 'Recipient',
    'CreatedAt': '2019-12-17T08:58:33-05:00'
}
```

Filters: `SuppressionReason` (`HardBounce`, `SpamComplaint`,
`ManualSuppression`), `Origin` (`Recipient`, `Customer`, `Admin`), `fromdate`,
`todate` and `EmailAddress`.

## Suppress addresses

Up to 50 addresses per call. Each address gets its own status:

```python
>>> postmark.suppressions.create(
...     ["good.address@wildbit.com", "invalid-email-address"]
... )
[
    {
        'EmailAddress': 'good.address@wildbit.com',
        'Status': 'Suppressed',
        'Message': None
    },
    {
        'EmailAddress': 'invalid-email-address',
        'Status': 'Failed',
        'Message': 'An invalid email address was provided.'
    }
]
```

## Reactivate addresses

Up to 50 addresses per call. Deleting a `HardBounce` suppression reactivates
the bounce. `SpamComplaint` suppressions can't be deleted:

```python
>>> postmark.suppressions.delete(["good.address@wildbit.com"])
[
    {
        'EmailAddress': 'good.address@wildbit.com',
        'Status': 'Deleted',
        'Message': None
    }
]
```
