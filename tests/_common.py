"""
Shared helpers for the demo / example scripts under tests/.

Loads configuration from a project-root .env file (see .env.example) and
exposes small factory functions so each demo can stay focused on the API
it is demonstrating instead of repeating boilerplate.

Typical use in a demo script:

    from _common import make_client
    client = make_client()
    print(client.get_account_v3())
"""
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False

from apexomni.constants import (
    APEX_OMNI_HTTP_MAIN,
    APEX_OMNI_HTTP_TEST,
    APEX_OMNI_WS_MAIN,
    APEX_OMNI_WS_TEST,
    NETWORKID_MAIN,
    NETWORKID_TEST,
    NETWORKID_OMNI_MAIN_ARB,
    NETWORKID_OMNI_TEST_BNB,
)
from apexomni.http_public import HttpPublic
from apexomni.http_private_v3 import HttpPrivate_v3
from apexomni.http_private_sign import HttpPrivateSign, HttpPrivateRwaSign


# Make the project root importable so demos can `from _common import ...`
# regardless of where they are invoked from.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

load_dotenv(os.path.join(_ROOT, ".env"))


_PLACEHOLDERS = ("your ", "<", "todo")


def _looks_unset(val):
    if not val:
        return True
    low = val.lower()
    return any(low.startswith(p) for p in _PLACEHOLDERS)


def require(name):
    """Return env var `name`, or exit with a friendly setup message."""
    val = os.getenv(name, "").strip()
    if _looks_unset(val):
        raise SystemExit(
            f"\n[setup] Missing env var: {name}\n"
            f"        Copy .env.example to .env at the project root and fill it in.\n"
        )
    return val


def optional(name, default=None):
    """Return env var `name` if it looks set, else `default`. No exit."""
    val = os.getenv(name, "").strip()
    if _looks_unset(val):
        return default
    return val


def env_network():
    """Return ('endpoint', network_id, chain_id) for the configured environment."""
    env = os.getenv("APEX_ENV", "test").strip().lower()
    if env == "main":
        return APEX_OMNI_HTTP_MAIN, NETWORKID_MAIN, NETWORKID_OMNI_MAIN_ARB
    return APEX_OMNI_HTTP_TEST, NETWORKID_TEST, NETWORKID_OMNI_TEST_BNB


def env_ws_endpoint():
    """Return the WebSocket endpoint for the configured environment."""
    env = os.getenv("APEX_ENV", "test").strip().lower()
    return APEX_OMNI_WS_MAIN if env == "main" else APEX_OMNI_WS_TEST


def _api_credentials():
    return {
        "key":        require("APEX_API_KEY"),
        "secret":     require("APEX_API_SECRET"),
        "passphrase": require("APEX_API_PASSPHRASE"),
    }


def make_client(preload=True):
    """
    Return a ready-to-use HttpPrivate_v3 client for queries / transfers /
    registration follow-ups. If `preload` is True (default) the client's
    configV3 and accountV3 caches are warmed up before returning.

    Requires: APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE,
    plus ETH_PRIVATE_KEY when on-chain signing is needed.
    """
    endpoint, network_id, _chain_id = env_network()
    client = HttpPrivate_v3(
        endpoint,
        network_id=network_id,
        eth_private_key=optional("ETH_PRIVATE_KEY"),
        api_key_credentials=_api_credentials(),
    )
    if preload:
        client.configs_v3()
        client.get_account_v3()
    return client


def make_signing_client(preload=True):
    """
    Return an HttpPrivateSign client wired with the ZK keys needed to sign
    order placement / withdrawals. Same env requirements as make_client(),
    plus APEX_ZK_SEEDS and APEX_ZK_L2KEY.
    """
    endpoint, network_id, _chain_id = env_network()
    client = HttpPrivateSign(
        endpoint,
        network_id=network_id,
        zk_seeds=require("APEX_ZK_SEEDS"),
        zk_l2Key=require("APEX_ZK_L2KEY"),
        eth_private_key=optional("ETH_PRIVATE_KEY"),
        api_key_credentials=_api_credentials(),
    )
    if preload:
        client.configs_v3()
        client.get_account_v3()
    return client


def make_rwa_client(preload=True):
    """
    Return an HttpPrivateRwa_v3 client defaulted to the RWA account.
    Requires the APEX_RWA_* env vars in addition to the primary credentials.
    """
    endpoint, network_id, _chain_id = env_network()
    client = HttpPrivateRwa_v3(
        endpoint,
        network_id=network_id,
        eth_private_key=optional("ETH_PRIVATE_KEY"),
        api_key_credentials=_api_credentials(),
    )
    client.set_rwa_api_credentials({
        "key":        require("APEX_RWA_API_KEY"),
        "secret":     require("APEX_RWA_API_SECRET"),
        "passphrase": require("APEX_RWA_API_PASSPHRASE"),
    })
    if preload:
        client.configs_v3()
        client.get_account_v3()
    return client


def make_rwa_signing_client(preload=True):
    """
    Return an HttpPrivateRwaSign client — combines RWA account context with
    the ZK seeds needed to sign RWA orders / transfers. Auto-generates an
    RWA API credential set via /stock/generate-api if APEX_RWA_API_* are
    not present.
    """
    endpoint, network_id, _chain_id = env_network()
    client = HttpPrivateRwaSign(
        endpoint,
        network_id=network_id,
        zk_seeds=require("APEX_ZK_SEEDS"),
        zk_l2Key=require("APEX_ZK_L2KEY"),
        eth_private_key=optional("ETH_PRIVATE_KEY"),
        api_key_credentials=_api_credentials(),
    )
    rwa_key = optional("APEX_RWA_API_KEY")
    if rwa_key:
        client.set_rwa_api_credentials({
            "key":        rwa_key,
            "secret":     require("APEX_RWA_API_SECRET"),
            "passphrase": require("APEX_RWA_API_PASSPHRASE"),
        })
    if preload:
        client.configs_v3()
        client.get_account_v3()
    return client


def make_public_client():
    """Return an HttpPublic client for market-data demos (no credentials)."""
    endpoint, _network_id, _chain_id = env_network()
    return HttpPublic(endpoint)


def banner(title):
    """Print a labelled section banner — keeps demo output scannable."""
    bar = "─" * max(8, 60 - len(title))
    print(f"\n── {title} {bar}")
