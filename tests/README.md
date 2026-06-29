# Demos & Examples

This folder doubles as the example gallery and the smoke-test suite for the
`apexomni` SDK. Each script demonstrates a single end-to-end flow against
Apex Omni V3 (mainnet or testnet, your choice).

## First-time setup

```bash
# 1. Install the SDK with demo + test extras (or just run `make setup`)
pip install -e ".[demos,tests]"

# 2. Copy the env template and fill it in
cp .env.example .env
$EDITOR .env            # set ETH_PRIVATE_KEY, choose APEX_ENV=test|main
```

That is the only setup. Every demo loads its configuration from `.env` —
no source-file editing required.

## Recommended order (V3 happy path)

| Step | Script                                | What it does                                            | Needs in .env                                |
|------|---------------------------------------|---------------------------------------------------------|----------------------------------------------|
| 1    | `01_register_v3.py`                   | Register a new V3 account; prints API keys + ZK seeds   | `ETH_PRIVATE_KEY`                            |
| 2    | _(copy keys from step 1 output)_      | Paste the printed values into `.env`                    | `APEX_API_*`, `APEX_ZK_*`                    |
| 3    | `02_public_v3.py`                     | Public market data (no auth)                            | —                                            |
| 4    | `03_private_v3.py`                    | Read account / positions / fills / orders / PnL         | `APEX_API_*`                                 |
| 5    | `04_create_order_v3.py`               | Place perpetual orders (limit, conditional, MARKET, TP/SL) | `APEX_API_*`, `APEX_ZK_*`                |
| 6    | `05_transfer_v3.py`                   | Fund ↔ contract transfers & withdrawals                 | `APEX_API_*`, `APEX_ZK_*`                    |
| 7    | `06_private_apikeys_v3.py`            | List / generate additional API keys                     | `APEX_API_*`, `APEX_ZK_*`                    |

### Multi-address (LP) registration

| Step | Script                                | What it does                                            | Needs in .env                                |
|------|---------------------------------------|---------------------------------------------------------|----------------------------------------------|
| 1    | `07_register_mul_address_step1.py`    | Register an LP account bound to a secondary ETH address | `ETH_PRIVATE_KEY`, `APEX_MUL_ETH_ADDRESS`    |
| 2    | `08_register_mul_address_step2.py`    | Activate the LP account (on-chain signature)            | `APEX_API_*`, `APEX_ZK_*`, `APEX_ZK_PUBKEY_HASH` |

### RWA sub-account

| Step | Script                                | What it does                                            | Needs in .env                                |
|------|---------------------------------------|---------------------------------------------------------|----------------------------------------------|
| 1    | `10_rwa_register.py`                  | Register RWA account, generate RWA API keys             | `APEX_API_*`, `APEX_ZK_*`                    |
| 2    | `11_rwa_transfer.py`                  | Contract ↔ RWA transfers (and optional out-to-address)  | `APEX_RWA_API_*`                             |
| 3    | `12_rwa_create_order.py`              | Place an RWA limit order (e.g. AAPL-USDT)               | `APEX_RWA_API_*`                             |

### Streaming

| Script                                | What it does                                                   | Needs in .env                                |
|---------------------------------------|----------------------------------------------------------------|----------------------------------------------|
| `20_ws_account_v3.py`                 | Subscribe to V3 account / trade / kline WebSocket streams      | `APEX_API_*`                                 |

## Smoke tests

```bash
pytest tests/
```

`test_demos_smoke.py` parses every numbered demo and exercises the
`_common.py` helpers — no network calls, no API keys required, just a
sanity check that the demo set is in a runnable state.

## Legacy demos (V1 / V2)

Older demos targeting the V1 STARK-based and V2 APIs live under
`tests/legacy/`. They are kept for reference and still use the original
hardcoded-credentials pattern. For new integrations, use the numbered
V3 demos above.

## Running a demo

```bash
python tests/01_register_v3.py
```

Every migrated demo:

- Loads config from `.env` via `_common.py`.
- Fails fast with a friendly setup hint if a required variable is missing.
- Wraps the example in a `main()` function with an `if __name__ == "__main__":`
  guard, so it can be imported by tests or invoked as a script.

## Environments

`APEX_ENV=test` (default) targets the BNB testnet endpoint, `APEX_ENV=main`
targets the Arbitrum mainnet endpoint. The helper picks the right URL,
network id, and chain id for you.

## Programmatic use

```python
from tests._common import make_client, make_signing_client

client = make_client()                 # for queries / transfers / registration
client.get_account_v3()

signer = make_signing_client()         # for order placement / withdrawals
signer.create_order_v3(symbol="BTC-USDT", side="BUY", type="LIMIT",
                       size="0.01", price="20000")
```

