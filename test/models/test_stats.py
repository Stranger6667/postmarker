import pytest

CASSETTE_NAME = "stats"


@pytest.mark.parametrize(
    "method, kwargs, expected",
    (
        (
            "overview",
            {"fromdate": "2017-01-30"},
            {
                "BounceRate": 0.0,
                "Bounced": 0,
                "Opens": 50,
                "SMTPApiErrors": 0,
                "Sent": 93,
                "SpamComplaints": 0,
                "SpamComplaintsRate": 0.0,
                "TotalClicks": 0,
                "TotalTrackedLinksSent": 0,
                "Tracked": 93,
                "UniqueLinksClicked": 0,
                "UniqueOpens": 19,
                "WithClientRecorded": 13,
                "WithLinkTracking": 0,
                "WithOpenTracking": 93,
                "WithPlatformRecorded": 19,
                "WithReadTimeRecorded": 19,
            },
        ),
        (
            "sends",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "Sent": 37},
                    {"Date": "2017-01-31", "Sent": 54},
                    {"Date": "2017-02-01", "Sent": 2},
                ],
                "Sent": 93,
            },
        ),
        ("bounces", {"fromdate": "2017-01-30"}, {"Days": []}),
        ("spam", {"fromdate": "2017-01-30"}, {"Days": []}),
        (
            "tracked",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "Tracked": 37},
                    {"Date": "2017-01-31", "Tracked": 54},
                    {"Date": "2017-02-01", "Tracked": 2},
                ],
                "Tracked": 93,
            },
        ),
        (
            "opens",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "Opens": 6, "Unique": 3},
                    {"Date": "2017-01-31", "Opens": 39, "Unique": 13},
                    {"Date": "2017-02-01", "Opens": 5, "Unique": 3},
                ],
                "Opens": 50,
                "Unique": 19,
            },
        ),
        (
            "opens_platforms",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "Desktop": 1, "Mobile": 1, "Unknown": 1},
                    {"Date": "2017-01-31", "Desktop": 2, "Unknown": 11},
                    {"Date": "2017-02-01", "Unknown": 3},
                ],
                "Desktop": 3,
                "Mobile": 1,
                "Unknown": 15,
            },
        ),
        (
            "emailclients",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "Gmail": 1, "Thunderbird": 1},
                    {"Date": "2017-01-31", "Gmail": 6, "Thunderbird": 2},
                    {"Date": "2017-02-01", "Gmail": 3},
                ],
                "Gmail": 10,
                "Thunderbird": 3,
            },
        ),
        (
            "readtimes",
            {"fromdate": "2017-01-30"},
            {
                "Days": [
                    {"Date": "2017-01-30", "0s": 1, "16s": 1, "unknown": 1},
                    {
                        "Date": "2017-01-31",
                        "20s+": 2,
                        "4s": 2,
                        "8s": 1,
                        "9s": 2,
                        "unknown": 6,
                    },
                    {"Date": "2017-02-01", "unknown": 3},
                ],
                "0s": 1,
                "16s": 1,
                "20s+": 2,
                "4s": 2,
                "8s": 1,
                "9s": 2,
                "unknown": 10,
            },
        ),
        ("clicks", {}, {"Days": []}),
        ("browserfamilies", {}, {"Days": []}),
        ("clicks_platforms", {}, {"Days": []}),
        ("location", {}, {"Days": []}),
    ),
)
def test_methods(postmark, method, kwargs, expected):
    assert getattr(postmark.stats, method)(**kwargs) == expected
