"""Each request sends its own client's token (no network: the HTTP session is stubbed)."""

import time
from unittest.mock import MagicMock

import pytest
from garth.auth_tokens import OAuth1Token, OAuth2Token

import garminconnect


def _client(name: str) -> garminconnect.Garmin:
    client = garminconnect.Garmin()
    client.garth.oauth1_token = OAuth1Token(oauth_token=name, oauth_token_secret="secret")
    now = int(time.time())
    client.garth.oauth2_token = OAuth2Token(
        scope="", jti="", token_type="Bearer", access_token=f"token-of-{name}",
        refresh_token="refresh", expires_in=3600, expires_at=now + 3600,
        refresh_token_expires_in=7200, refresh_token_expires_at=now + 7200,
    )
    client.garth.sess = MagicMock()
    client.garth.sess.request.return_value = MagicMock(status_code=200, json=lambda: {})
    return client


def _sent_authorization(client: garminconnect.Garmin) -> str | None:
    return client.garth.sess.request.call_args.kwargs["headers"].get("Authorization")


@pytest.mark.parametrize("call", [
    lambda c: c.query_garmin_graphql({"query": "query{x}"}),
    lambda c: c.add_gear_to_activity("uuid", 1),
    lambda c: c.remove_gear_from_activity("uuid", 1),
    lambda c: c.add_hydration_data(250, cdate="2026-10-01", timestamp="2026-10-01T08:00:00.000"),
])
def test_a_call_sends_its_own_token_not_the_last_one_of_the_process(call):
    """garth shares one default headers dict between all calls: before the fix, Bob's
    GraphQL call sent Alice's token (and a stale one gave HTTP 401 after a long idle)."""
    alice, bob = _client("alice"), _client("bob")
    alice.connectapi("/usersummary-service/x")
    call(bob)
    assert _sent_authorization(bob) == "Bearer token-of-bob"


def test_a_request_without_api_leaves_no_token_behind():
    alice = _client("alice")
    alice.connectapi("/usersummary-service/x")
    alice.garth.get("connect", "/public-page")
    assert _sent_authorization(alice) is None
