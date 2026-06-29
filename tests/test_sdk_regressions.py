"""
Regression tests for SDK behavior that has been broken in the past.

Each test pins a specific invariant a previous refactor accidentally
removed; if any of them fails, look at the linked commit before
"fixing" by deleting the assertion.

  - change_pub_key_v3 must live on HttpPrivate_v3 (regression from the
    RWA / stock refactor that nested 30+ methods inside the subclass).
  - HttpPrivateSign.create_order_v3 must lazy-load configV3 and accountV3
    so callers can place orders without remembering the prep dance.
"""
import pytest

from apexomni.http_private_sign import HttpPrivateSign
from apexomni.http_private_v3 import HttpPrivate_v3, HttpPrivateRwa_v3


# ── class membership ────────────────────────────────────────────────────

def test_change_pub_key_v3_is_on_httpprivate_v3():
    """Customer flow `HttpPrivate_v3(...).change_pub_key_v3(...)` must work."""
    assert "change_pub_key_v3" in vars(HttpPrivate_v3), (
        "change_pub_key_v3 was previously trapped inside HttpPrivateRwa_v3; "
        "see commit that restored generic v3 methods to HttpPrivate_v3."
    )


def test_rwa_subclass_inherits_change_pub_key_v3():
    """RWA users still get change_pub_key_v3 via inheritance."""
    assert callable(getattr(HttpPrivateRwa_v3, "change_pub_key_v3", None))


@pytest.mark.parametrize("method", [
    "transfer_v3", "fills_v3", "open_orders_v3", "delete_order_v3",
    "withdraw_fee_v3", "all_apikeys_v3", "generate_api_key_v3",
    "get_credit_account_v3",
])
def test_generic_methods_on_httpprivate_v3(method):
    """A spot-check that the rest of the moved methods landed on the parent."""
    assert method in vars(HttpPrivate_v3), f"{method} not on HttpPrivate_v3"


# ── lazy-load helpers ───────────────────────────────────────────────────

class _StubClient(HttpPrivateSign):
    """HttpPrivateSign without any network or credential setup."""

    def __init__(self):  # noqa: D401 — intentionally bypass parent __init__
        self.accountV3 = None
        self.configV3 = None
        self._default_account_type = "primary"
        self.calls = []

    def get_account_v3(self, account_type="primary", **_):
        self.calls.append(("get_account_v3", account_type))
        self.accountV3 = {"id": "stub", "contractAccount": {"takerFeeRate": "0.0005"}}
        return self.accountV3

    def configs_v3(self, **_):
        self.calls.append(("configs_v3",))
        self.configV3 = {"contractConfig": {"perpetualContract": []}}
        return {"data": self.configV3}


def test_ensure_account_snapshot_auto_fetches():
    """When accountV3 is empty, _ensure_account_snapshot calls get_account_v3."""
    c = _StubClient()
    out = c._ensure_account_snapshot()
    assert out["id"] == "stub"
    assert ("get_account_v3", "primary") in c.calls


def test_ensure_account_snapshot_no_refetch_when_cached():
    """If accountV3 is already cached, _ensure_account_snapshot reuses it."""
    c = _StubClient()
    c.accountV3 = {"id": "cached"}
    out = c._ensure_account_snapshot()
    assert out["id"] == "cached"
    assert c.calls == []  # no network call


def test_ensure_account_snapshot_raises_when_server_returns_nothing():
    """A friendlier error than the old AttributeError when fetch fails."""
    class FailingStub(_StubClient):
        def get_account_v3(self, account_type="primary", **_):
            self.calls.append(("get_account_v3", account_type))
            return None

    c = FailingStub()
    with pytest.raises(Exception, match="Failed to fetch account data"):
        c._ensure_account_snapshot()


def test_ensure_config_v3_auto_fetches():
    """When configV3 is empty, _ensure_config_v3 calls configs_v3."""
    c = _StubClient()
    out = c._ensure_config_v3()
    assert "contractConfig" in out
    assert ("configs_v3",) in c.calls


def test_ensure_config_v3_no_refetch_when_cached():
    """If configV3 is already cached, _ensure_config_v3 reuses it."""
    c = _StubClient()
    c.configV3 = {"contractConfig": {"perpetualContract": ["something"]}}
    out = c._ensure_config_v3()
    assert out is c.configV3
    assert c.calls == []


def test_ensure_config_v3_raises_when_server_returns_nothing():
    """Surface a clear error if configs_v3 silently fails."""
    class FailingStub(_StubClient):
        def configs_v3(self, **_):
            self.calls.append(("configs_v3",))
            # don't update self.configV3 — simulates a silent server miss

    c = FailingStub()
    with pytest.raises(Exception, match="Failed to fetch configV3"):
        c._ensure_config_v3()
