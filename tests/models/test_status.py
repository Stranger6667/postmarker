# coding: utf-8
from postmarker.models.status import Incident


CASSETTE_NAME = "status"

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


def test_status(postmark):
    assert postmark.status.get() == {"lastCheckDate": "2016-10-09T11:48:21Z", "status": "UP"}


def test_last_incident(postmark):
    incident = postmark.status.incidents.last
    assert isinstance(incident, Incident)
    assert incident.as_dict() == LAST_INCIDENT
    assert str(incident) == "Incident: 1965"


def test_incidents(postmark):
    incidents = postmark.status.incidents.all()
    assert all(isinstance(incident, Incident) for incident in incidents)


def test_get_incident(postmark):
    incident = postmark.status.incidents.get(1965)
    assert isinstance(incident, Incident)
    assert incident.as_dict() == LAST_INCIDENT


def test_services(postmark):
    assert postmark.status.services == [
        {"status": "UP", "url": "/services/api", "name": "API Response Time"},
        {"status": "UP", "url": "/services/smtp", "name": "SMTP Response Time"},
        {"status": "UP", "url": "/services/web", "name": "Web Response Time"},
        {"status": "UP", "url": "/services/inbound", "name": "Inbound SMTP Response Time"},
    ]


def test_availability(postmark):
    assert postmark.status.availability == {
        "fromDate": "2016-07-11T11:47:10.371Z",
        "percentageUp": 0.9998308505688754,
        "secondsDown": 5280,
        "secondsUp": 31209723,
        "toDate": "2016-10-09T11:47:10.372Z",
    }


def test_delivery(postmark):
    assert postmark.status.delivery == [
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "AOL"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Apple"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Gmail"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Hotmail"},
        {"missing": 0, "spf": 1, "spam": 0, "inbox": 1, "dkim": 1, "name": "Yahoo!"},
    ]
