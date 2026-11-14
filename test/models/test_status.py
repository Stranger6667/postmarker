import pytest

from postmarker.models.status import Incident

from ..conftest import aw

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]

LAST_INCIDENT = {
    "body": "",
    "created_at": "2016-10-08T02:11:00+00:00",
    "id": "1965",
    "resolved_at": "2016-10-08T02:31:00+00:00",
    "title": "Delaying in inbound and outbound processing",
    "type": "DEGRADED",
    "updated_at": "2016-10-08T02:31:00+00:00",
    "updates": [
        {
            "status": "Investigating",
            "body": "We're queueing up messages to be processed, affecting inbound and outbound traffic. "
            "We're working to resolve ASAP.",
            "timestamp": "2016-10-08T02:11:00+00:00",
        },
        {
            "status": "Pending",
            "body": "Outbound and inbound messages should be back to getting processed immediately and "
            "saved jobs are all processed. We're continuing to monitor the situation.",
            "timestamp": "2016-10-08T02:20:00+00:00",
        },
        {
            "status": "Resolved",
            "body": "The issue has been resolved and all queues are back to normal.",
            "timestamp": "2016-10-08T02:31:00+00:00",
        },
    ],
}


async def test_status(client):
    assert await aw(client.status.get()) == {
        "lastCheckDate": "2016-10-09T11:48:21Z",
        "status": "UP",
    }


async def test_last_incident(client):
    incident = await aw(client.status.incidents.last)
    assert isinstance(incident, Incident)
    assert incident.as_dict() == LAST_INCIDENT
    assert str(incident) == "Incident: 1965"


async def test_incidents(client):
    incidents = await aw(client.status.incidents.all())
    assert all(isinstance(incident, Incident) for incident in incidents)


async def test_get_incident(client):
    incident = await aw(client.status.incidents.get(1965))
    assert isinstance(incident, Incident)
    assert incident.as_dict() == LAST_INCIDENT


async def test_services(client):
    assert await aw(client.status.services) == [
        {"status": "UP", "url": "/services/api", "name": "API Response Time"},
        {"status": "UP", "url": "/services/smtp", "name": "SMTP Response Time"},
        {"status": "UP", "url": "/services/web", "name": "Web Response Time"},
        {
            "status": "UP",
            "url": "/services/inbound",
            "name": "Inbound SMTP Response Time",
        },
    ]


async def test_availability(client):
    assert await aw(client.status.availability) == {
        "fromDate": "2016-07-11T11:47:10.371Z",
        "percentageUp": 0.9998308505688754,
        "secondsDown": 5280,
        "secondsUp": 31209723,
        "toDate": "2016-10-09T11:47:10.372Z",
    }


async def test_delivery(client):
    assert await aw(client.status.delivery) == [
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "AOL"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Apple"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Gmail"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Hotmail"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Yahoo!"},
    ]
