# API Reference

`PostmarkClient` exposes each Postmark API as a manager, e.g. `postmark.templates`.
Managers return models. Each Postmark field of a model is an attribute with the same name, e.g. `template.Name`.

## Client

::: postmarker.core.PostmarkClient
    options:
      merge_init_into_class: true
      members: [from_config, spamcheck]

## Emails

`postmark.emails`, see [Emails](emails.md).

::: postmarker.models.emails.EmailManager
    options:
      members: [send, send_with_template, send_batch, send_template_batch, Email, EmailTemplate, EmailBatch, EmailTemplateBatch]

::: postmarker.models.emails.Email
    options:
      members: [attach, attach_binary, send]
      inherited_members: [attach, attach_binary]

::: postmarker.models.emails.EmailTemplate
    options:
      members: [attach, attach_binary, send]
      inherited_members: [attach, attach_binary]

## Templates

`postmark.templates`, see [Templates](templates.md). `push` needs the account token.

::: postmarker.models.templates.TemplateManager
    options:
      members: [all, get, create, edit, delete, validate, push]

::: postmarker.models.templates.Template
    options:
      members: [get, edit, delete]

## Bounces

`postmark.bounces`, see [Bounces](bounces.md).

::: postmarker.models.bounces.BounceManager

::: postmarker.models.bounces.Bounce
    options:
      members: [dump, activate, message]
      inherited_members: [message]

## Messages

`postmark.messages.outbound`, `postmark.messages.outbound.opens` and `postmark.messages.inbound`, see [Messages](messages.md).

::: postmarker.models.messages.OutboundMessageManager
    options:
      members: [all, get, get_dump]

::: postmarker.models.messages.OutboundMessage
    options:
      members: [get, get_dump, opens]
      inherited_members: [get]

::: postmarker.models.messages.OpensManager
    options:
      members: [all, get, Open]

::: postmarker.models.messages.InboundMessageManager
    options:
      members: [all, get, bypass, retry, InboundMessage]

::: postmarker.models.messages.InboundMessage
    options:
      members: [get, bypass, retry, as_mime, Attachments]
      inherited_members: [get]

::: postmarker.models.messages.Attachment
    options:
      members: [decoded, save, as_mime]

## Message Streams

`postmark.message_streams`, see [Message Streams](message_streams.md).

::: postmarker.models.message_streams.MessageStreamsManager
    options:
      members: [all, get, create, edit, archive, unarchive]

::: postmarker.models.message_streams.MessageStream
    options:
      members: [get, edit, archive, unarchive]

## Sender signatures

`postmark.senders`, see [Sender signatures](sender_signatures.md). Needs the account token.

::: postmarker.models.senders.SenderSignaturesManager
    options:
      members: [all, get, create, edit, delete, resend, verifyspf]

::: postmarker.models.senders.SenderSignature
    options:
      members: [get, edit, delete, resend, verifyspf]

## Server

`postmark.server`, see [Server](server.md).

::: postmarker.models.server.ServerManager
    options:
      members: [get, edit]

::: postmarker.models.server.Server
    options:
      members: [edit]

## Servers

`postmark.servers`, see [Servers](servers.md). Needs the account token.

::: postmarker.models.servers.ServersManager
    options:
      members: [all, get, create, edit, delete]

::: postmarker.models.servers.AccountServer
    options:
      members: [get, edit, delete]

## Status

`postmark.status` and `postmark.status.incidents`, see [Status](status.md).

::: postmarker.models.status.StatusManager
    options:
      members: [get, services, availability, delivery]

::: postmarker.models.status.IncidentsManager
    options:
      members: [all, get, last]

## Stats

`postmark.stats`, see [Stats](stats.md).

::: postmarker.models.stats.StatsManager

## Triggers

`postmark.triggers.inboundrules` and `postmark.triggers.tags`, see [Triggers](triggers.md).

::: postmarker.models.triggers.InboundRulesManager
    options:
      members: [all, create, delete]

::: postmarker.models.triggers.InboundRule
    options:
      members: [delete]

::: postmarker.models.triggers.TagsTriggersManager
    options:
      members: [all, get, create, edit, delete]

::: postmarker.models.triggers.Tag
    options:
      members: [get, edit, delete]

## Suppressions

`postmark.suppressions`, see [Suppressions](suppressions.md).

::: postmarker.models.suppressions.SuppressionsManager

## Domains

`postmark.domains`, see [Domains](domains.md). Needs the account token.

::: postmarker.models.domains.DomainsManager
    options:
      members: [all, get, create, edit, delete, verifyspf, verifydkim, verifyreturnpath, rotatedkim]

::: postmarker.models.domains.Domain
    options:
      members: [get, edit, delete, verifyspf, verifydkim, verifyreturnpath, rotatedkim]
