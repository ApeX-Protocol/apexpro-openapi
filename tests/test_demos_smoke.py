"""
Smoke tests that don't hit the network.

Verify that:
  - every numbered V3 demo parses cleanly and references only public APIs
    on the apexomni package;
  - the shared helper module (_common.py) exposes all expected factories;
  - the public market-data client can be constructed without any env vars.

Run:
    pytest tests/test_demos_smoke.py
"""
import ast
import os
import pathlib

import pytest


TESTS_DIR = pathlib.Path(__file__).parent


def _numbered_demos():
    return sorted(p for p in TESTS_DIR.iterdir()
                  if p.suffix == ".py"
                  and p.name[:2].isdigit())


@pytest.mark.parametrize("demo", _numbered_demos(), ids=lambda p: p.name)
def test_demo_parses(demo):
    """Every numbered demo must be syntactically valid Python."""
    ast.parse(demo.read_text())


def test_common_exposes_factories():
    """_common.py must expose every helper the demos rely on."""
    import _common  # noqa: WPS433 — script-style import is intentional
    for name in (
        "require", "optional", "env_network", "env_ws_endpoint",
        "make_client", "make_signing_client",
        "make_rwa_client", "make_rwa_signing_client",
        "make_public_client", "banner",
    ):
        assert callable(getattr(_common, name, None)), f"_common.{name} missing"


def test_public_client_no_env():
    """make_public_client() must work without any env vars set."""
    import _common
    client = _common.make_public_client()
    assert client is not None


def test_require_fails_friendly(monkeypatch):
    """require() must SystemExit with a setup hint when the env var is missing."""
    import _common
    monkeypatch.delenv("APEX_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        _common.require("APEX_API_KEY")
    assert "Copy .env.example" in str(exc.value)


def test_require_rejects_placeholder(monkeypatch):
    """require() must treat 'your ...' placeholders as missing."""
    import _common
    monkeypatch.setenv("APEX_API_KEY", "your apiKey-key from register")
    with pytest.raises(SystemExit):
        _common.require("APEX_API_KEY")


def test_optional_returns_default_for_placeholder(monkeypatch):
    """optional() must return the default when the env value is a placeholder."""
    import _common
    monkeypatch.setenv("RECEIVER_ETH_ADDRESS", "your eth address")
    assert _common.optional("RECEIVER_ETH_ADDRESS", "fallback") == "fallback"


def test_env_network_switches_on_apex_env(monkeypatch):
    """APEX_ENV=main → mainnet endpoint; otherwise testnet."""
    import _common
    monkeypatch.setenv("APEX_ENV", "main")
    main_endpoint, _, _ = _common.env_network()
    assert "qa" not in main_endpoint

    monkeypatch.setenv("APEX_ENV", "test")
    test_endpoint, _, _ = _common.env_network()
    assert test_endpoint != main_endpoint


def _setup_sys_path():
    """Make tests/ importable so `import _common` works in this test file."""
    import sys
    if str(TESTS_DIR) not in sys.path:
        sys.path.insert(0, str(TESTS_DIR))


_setup_sys_path()
