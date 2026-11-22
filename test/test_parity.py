import contextlib
import datetime
import importlib
import inspect
import pkgutil
import re
from typing import is_typeddict

import pytest

import postmarker.core
import postmarker.models
from postmarker.core import AsyncPostmarkClient, PostmarkClient

from .conftest import aw

MODULES = [postmarker.core] + [
    importlib.import_module(f"postmarker.models.{module.name}")
    for module in pkgutil.iter_modules(postmarker.models.__path__)
]
# Classes that make no requests; both clients share them
NO_REQUESTS = {"Model", "Suppression", "Incident", "Attachment"}
ASYNC_ONLY = {"aclose", "__aenter__", "__aexit__"}
# Members a twin defines itself without being a coroutine: they make no requests
SYNC_ON_TWIN = {"__init__", "session", "check_response", "SpamComplaint", "SubscriptionChange"}
# The transport's response type differs by design
ANNOTATION_EXCEPTIONS = {"check_response"}


def classes(module):
    return [
        cls
        for name, cls in vars(module).items()
        if inspect.isclass(cls)
        and not is_typeddict(cls)
        and cls.__module__ == module.__name__
        and not name.startswith(("Async", "Base", "_"))
    ]


def find_pairs():
    pairs, missing = [], []
    for module in MODULES:
        for cls in classes(module):
            twin = getattr(module, f"Async{cls.__name__}", None)
            if twin is not None:
                pairs.append((cls, twin))
            elif cls.__name__ not in NO_REQUESTS:
                missing.append(f"{module.__name__}.{cls.__name__}")
    return pairs, missing


PAIRS, MISSING = find_pairs()
TWINNED = {sync_cls.__name__ for sync_cls, _ in PAIRS}


def as_async(annotation):
    # Lookarounds keep string values such as `Literal['SpamComplaint']` intact
    return re.sub(rf"(?<!')\b({'|'.join(TWINNED)})\b(?!')", r"Async\1", annotation)


def public_members(cls):
    return {name for name in dir(cls) if not name.startswith("_")} | {"__init__"}


def signature(member):
    target = member.fget if isinstance(member, property) else member
    return inspect.signature(target)


def is_coroutine(member):
    target = member.fget if isinstance(member, property) else member
    return inspect.iscoroutinefunction(target)


def assert_parity(sync_cls, async_cls):
    assert public_members(sync_cls) == public_members(async_cls) - ASYNC_ONLY
    for name in public_members(sync_cls):
        sync_member, async_member = getattr(sync_cls, name), getattr(async_cls, name)
        if isinstance(sync_member, type):
            # A twin, or the same class when it makes no requests
            assert async_member is sync_member or async_member.__name__ == f"Async{sync_member.__name__}", name
        elif callable(sync_member) or isinstance(sync_member, property):
            sync_parameters = signature(sync_member).parameters.values()
            async_parameters = signature(async_member).parameters.values()
            assert [(p.name, p.kind, p.default) for p in sync_parameters] == [
                (p.name, p.kind, p.default) for p in async_parameters
            ], name
            if name not in ANNOTATION_EXCEPTIONS:
                assert [as_async(str(p.annotation)) for p in sync_parameters] == [
                    str(p.annotation) for p in async_parameters
                ], name
            shared = inspect.getattr_static(async_cls, name) is inspect.getattr_static(sync_cls, name)
            if not shared and name not in SYNC_ON_TWIN:
                assert is_coroutine(async_member), f"{async_cls.__name__}.{name} must be a coroutine"
        else:
            assert sync_member == async_member, name


def test_every_requesting_class_has_twin():
    assert MISSING == []


@pytest.mark.parametrize("sync_cls, async_cls", PAIRS, ids=[sync_cls.__name__ for sync_cls, _ in PAIRS])
def test_parity(sync_cls, async_cls):
    assert_parity(sync_cls, async_cls)


def test_client_managers_match():
    assert [m.name for m in AsyncPostmarkClient._managers] == [m.name for m in PostmarkClient._managers]


def requesting_members(owner, path=()):
    for manager_class in getattr(owner, "_managers", ()):
        if manager_class.name == "emails":
            # Sending needs a message; test_emails covers both clients
            continue
        manager = getattr(owner, manager_class.name)
        manager_path = (*path, manager_class.name)
        for name in sorted(public_members(type(manager)) - {"__init__", "call", "call_many"}):
            if is_coroutine(getattr(type(manager), name)):
                yield manager_path, name
        yield from requesting_members(manager, manager_path)


REQUESTING = list(requesting_members(AsyncPostmarkClient(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")))


def sample(parameter, position):
    """A distinct value per parameter, so a dropped or swapped argument changes the request."""
    annotation = str(parameter.annotation)
    if "date" in parameter.name.lower():
        return datetime.date(2020, 1, position + 1)
    if "bool" in annotation:
        return True
    if "int" in annotation:
        return position + 1
    if "list" in annotation:
        return [f"{parameter.name}@example.com"]
    if "dict" in annotation:
        return {parameter.name: position}
    return parameter.name


def invoke(owner, name):
    if isinstance(inspect.getattr_static(type(owner), name), property):
        return getattr(owner, name)
    member = getattr(owner, name)
    kwargs = {
        parameter.name: sample(parameter, position)
        for position, parameter in enumerate(signature(member).parameters.values())
        if parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
        and "Email" not in str(parameter.annotation)
    }
    return member(**kwargs)


@pytest.mark.anyio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("path, name", REQUESTING, ids=[".".join((*path, name)) for path, name in REQUESTING])
async def test_requests_match(postmark_request, postmark_async_request, path, name):
    calls = []
    for client_class, mock in ((PostmarkClient, postmark_request), (AsyncPostmarkClient, postmark_async_request)):
        owner = client_class(server_token="SERVER_TOKEN", account_token="ACCOUNT_TOKEN")
        for part in path:
            owner = getattr(owner, part)
        # Parsing the mocked response may fail; only the requests matter
        with contextlib.suppress(Exception):
            await aw(invoke(owner, name))
        calls.append(mock.call_args_list)
    assert calls[0]
    assert calls[0] == calls[1]
