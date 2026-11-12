# Checked by mypy as a downstream user would see the API; never executed.
from typing import Any

from postmarker.core import PostmarkClient
from postmarker.models.bounces import Bounce
from postmarker.models.emails import Email
from postmarker.models.messages import OutboundMessage

client = PostmarkClient(server_token="SERVER_TOKEN")
response: Any = client.emails.send(From="a@example.com", To="b@example.com", Subject="Hi", TextBody="Hi")
batch: Any = client.emails.send_batch({"From": "a@example.com", "To": "b@example.com", "TextBody": "Hi"})
bounce: Bounce = client.bounces.get(1)
bounce_id: int = bounce.ID
outbound: list[OutboundMessage] = client.messages.outbound.all()
opens: Any = client.messages.outbound.opens.all()
email: Email = client.emails.Email(From="a@example.com", To=["b@example.com", "c@example.com"], TextBody="Hi")
email.attach("readme.txt")
email["X-Accept-Language"] = "en-us, en"
template_response: Any = client.emails.send_with_template(
    TemplateId=1, TemplateModel={"name": "x"}, From="a@example.com", To="b@example.com"
)
last_incident = client.status.incidents.last
tags = client.triggers.tags.all()
inbound_rules = client.triggers.inboundrules.all()
