"""
Register the RWA sub-account and generate its API credentials.

Run this once before any other RWA demo. The printed APEX_RWA_API_* values
should be copied into .env so the other RWA demos can reuse them instead
of re-running /stock/generate-api on every invocation.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE   (primary)
    APEX_ZK_SEEDS / APEX_ZK_L2KEY

Run:
    python tests/10_rwa_register.py
"""
from _common import banner, make_rwa_signing_client


def main():
    client = make_rwa_signing_client()

    banner("register RWA account (idempotent)")
    print(client.register_rwa_account_v3())

    banner("generate RWA API key for wallet 'pythonSdk'")
    primary = client.get_account_v3() or {}
    eth_address = primary.get("ethereumAddress")
    gen = client.generate_rwa_api_v3(wallet_name="pythonSdk", eth_address=eth_address)
    print(gen)

    banner("loaded RWA account")
    rwa = client.get_account_v3_rwa() or {}
    print("RWA account id:", rwa.get("id"))

    banner("save into .env for the other RWA demos")
    api_key = ((gen or {}).get("data") or {}).get("apiKey") or {}
    if api_key:
        print(f"APEX_RWA_API_KEY={api_key.get('key', '')}")
        print(f"APEX_RWA_API_SECRET={api_key.get('secret', '')}")
        print(f"APEX_RWA_API_PASSPHRASE={api_key.get('passphrase', '')}")
    else:
        print("(no apiKey block in response — already registered? check response above)")


if __name__ == "__main__":
    main()
