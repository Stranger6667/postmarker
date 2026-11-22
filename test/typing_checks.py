# Checked by mypy as a downstream user would see the API; never executed.
from typing import Any

from postmarker.core import AsyncPostmarkClient, PostmarkClient
from postmarker.models.bounces import AsyncBounce, Bounce
from postmarker.models.emails import AsyncEmail, Email
from postmarker.models.messages import AsyncOutboundMessage, OutboundMessage

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
tracked: Any = client.emails.send(From="a@example.com", To="b@example.com", TextBody="Hi", TrackLinks="HtmlOnly")
mistyped: Any = client.emails.send(From="a@example.com", To="b@example.com", TextBody="Hi", TrackLinks="Html")  # type: ignore[arg-type]
template_response: Any = client.emails.send_with_template(
    TemplateId=1, TemplateModel={"name": "x"}, From="a@example.com", To="b@example.com"
)
last_incident = client.status.incidents.last
tags = client.triggers.tags.all()
inbound_rules = client.triggers.inboundrules.all()


async def _async_usage() -> None:
    async with AsyncPostmarkClient(server_token="SERVER_TOKEN") as async_client:
        async_response: Any = await async_client.call("GET", "/server")
        async_bounce: AsyncBounce = await async_client.bounces.get(1)
        async_dump: Any = await async_bounce.dump
        async_bounces: list[AsyncBounce] = await async_client.bounces.all()
        async_tags: Any = await async_client.triggers.tags.all()
        async_rules: Any = await async_client.triggers.inboundrules.all()
        async_last: Any = await async_client.status.incidents.last
        async_overview: Any = await async_client.stats.overview()
        async_outbound: list[AsyncOutboundMessage] = await async_client.messages.outbound.all()
        async_message: Any = await async_bounce.message
        async_email: AsyncEmail = async_client.emails.Email(From="a@example.com", To="b@example.com", TextBody="Hi")
        async_sent: Any = await async_email.send()
        async_sent_message: Any = await async_client.emails.send(message=async_email)
        async_batch: Any = await async_client.emails.send_batch({"From": "a@example.com", "To": "b@example.com"})
        async_template: Any = await async_client.emails.send_with_template(
            TemplateId=1, TemplateModel={}, From="a@example.com", To="b@example.com"
        )


# Send responses
sent = client.emails.send(From="a@example.com", To="b@example.com", TextBody="Hi")
sent_id: str = sent["MessageID"]
sent_typo = sent["MessageId"]  # type: ignore[typeddict-item]
batch_items = client.emails.send_batch({"From": "a@example.com", "To": "b@example.com", "TextBody": "Hi"})
batch_code: int = batch_items[0]["ErrorCode"]

attachment_dicts: list[dict[str, str]] = [{"Name": "a.txt", "Content": "YQ==", "ContentType": "text/plain"}]
with_attachments = client.emails.send(
    From="a@example.com", To="b@example.com", TextBody="Hi", Attachments=attachment_dicts
)

# Fixed-value parameters
suppressed = client.suppressions.all(SuppressionReason="HardBounce", Origin="Recipient")
bad_reason = client.suppressions.all(SuppressionReason="Bounce")  # type: ignore[arg-type]
results = client.suppressions.create(["a@example.com"])
result_status: str = results[0]["Status"]
layouts = client.templates.all(TemplateType="Layout")
bad_layout = client.templates.create(Name="x", HtmlBody="x", TemplateType="All")  # type: ignore[arg-type]
streams = client.message_streams.all(MessageStreamType="All")
bad_stream = client.message_streams.create(ID="x", Name="x", MessageStreamType="Inbound")  # type: ignore[arg-type]

# Server settings
account = PostmarkClient(account_token="ACCOUNT_TOKEN")
new_server = account.servers.create(Name="x", DeliveryType="Sandbox", TrackLinks="HtmlOnly")
account.servers.edit(1, InboundSpamThreshold=5)
account.servers.edit(1, DeliveryType="Live")  # type: ignore[call-arg]
client.server.edit(TrackOpens=True)
client.server.edit(TrackOpen=True)  # type: ignore[call-arg]
