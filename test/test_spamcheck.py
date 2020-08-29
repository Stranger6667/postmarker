import pytest

from postmarker.exceptions import SpamAssassinError

CASSETTE_NAME = "spamcheck"


EMAIL_DUMP = """Delivered-To: receiver@gmail.com
Received: by 10.194.205.41 with SMTP id ld9csp1978927wjc;
        Tue, 4 Oct 2016 01:34:04 -0700 (PDT)
X-Received: by 10.28.39.134 with SMTP id n128mr14037354wmn.60.1475570044702;
        Tue, 04 Oct 2016 01:34:04 -0700 (PDT)
Return-Path: <info@example.eu>
Received: from cloud1.example.io ([2a01:4f8:212:46::2])
        by mx.google.com with ESMTPS id da3si3018187wjc.119.2016.10.04.01.34.04
        for <receiver@gmail.com>
        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);
        Tue, 04 Oct 2016 01:34:04 -0700 (PDT)
Received-SPF: pass (google.com: domain of info@example.eu designates 2a01:4f8:212:46::2 as permitted sender)
client-ip=2a01:4f8:212:46::2;
Authentication-Results: mx.google.com;
       spf=pass (google.com: domain of info@example.eu designates 2a01:4f8:212:46::2 as permitted sender)
       smtp.mailfrom=info@example.eu
Received: from 0fdec0828b6b (unknown [172.17.2.33]) by cloud1.example.io (Postfix) with ESMTP id 645481AE0A73
for <receiver@gmail.com>; Tue,
  4 Oct 2016 10:34:04 +0200 (CEST)
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit
Subject: Recruiting Message from example.com
From: info@example.com
To: receiver@gmail.com
Date: Tue, 04 Oct 2016 08:34:04 -0000
Message-ID: <20161004083404.363.8793@0fdec0828b3b>

Bla bla bla,
"""


def test_spamcheck_valid(postmark):
    response = postmark.spamcheck(EMAIL_DUMP)
    assert response["success"]
    assert (
        response["report"]
        == """ pts rule name               description
---- ---------------------- --------------------------------------------------
 1.3 RDNS_NONE              Delivered to internal network by a host with no rDNS
 1.0 BODY_URI_ONLY          Message body is only a URI in one line of text or for
                            an image
 2.0 URI_ONLY_MSGID_MALF    URI only + malformed message ID

"""
    )


def test_spamcheck_invalid(postmark):
    with pytest.raises(SpamAssassinError) as exc:
        postmark.spamcheck("")
    assert str(exc.value) == "SpamAssassin error occured"
