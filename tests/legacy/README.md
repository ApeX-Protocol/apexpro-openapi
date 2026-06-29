# Legacy demos (V1 / V2)

These scripts target older versions of the Apex API (V1 STARK-based and V2)
and are kept for reference only. They use the original hardcoded-credentials
pattern (no `.env` support) — edit the constants at the top of each file
before running.

For new integrations, use the numbered V3 demos in the parent `tests/`
directory instead.

| File                              | What it does                              |
|-----------------------------------|-------------------------------------------|
| `demo_register.py`                | Register a V1 account                     |
| `demo_register_v2.py`             | Register a V2 account                     |
| `demo_register_mul_address.py`    | V1 multi-address registration             |
| `demo_public.py`                  | V1 public market data                     |
| `demo_public_v2.py`               | V2 public market data                     |
| `demo_private.py`                 | V1 private endpoints                      |
| `demo_private_v2.py`              | V2 private endpoints                      |
| `demo_stark_key_sign.py`          | V1 order placement via STARK signing      |
| `demo_stark_key_sign_v2.py`       | V2 order placement via STARK signing      |
| `demo_sign.py`                    | V1 STARK signing helpers                  |
| `demo_deposit.py`                 | V1 on-chain deposit flow                  |
| `demo_ws.py`                      | V1 WebSocket subscription                 |
| `demo_ws_v3.py`                   | Old V3 WebSocket sample (superseded by `20_ws_account_v3.py`) |
| `demo_ws_depthdata.py`            | V1 depth-stream sample                    |
| `account_value.py`                | V1 account-value calculation              |
| `account_value_ws.py`             | V1 account-value via WebSocket            |
