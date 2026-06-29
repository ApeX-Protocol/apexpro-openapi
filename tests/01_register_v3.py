"""
Step 1: register a new V3 account.

Derives ZK keys from your ETH private key, registers the account on Apex
Omni, and then calls change_pub_key_v3 to activate signing. The printed
output is what you need to paste into .env before running the other demos.

Prerequisites (in .env):
    ETH_PRIVATE_KEY     – your Ethereum private key (hex)
    APEX_ENV            – "test" (default) or "main"

Run:
    python tests/01_register_v3.py
"""
import time

from _common import banner, env_network, require
from apexomni.http_private_v3 import HttpPrivate_v3


def main():
    endpoint, network_id, chain_id = env_network()
    eth_private_key = require("ETH_PRIVATE_KEY")

    client = HttpPrivate_v3(endpoint, network_id=network_id, eth_private_key=eth_private_key)
    client.configs_v3()

    banner("derive ZK keys from ETH key")
    zk_keys = client.derive_zk_key(client.default_address)
    print("seeds      :", zk_keys["seeds"])
    print("l2Key      :", zk_keys["l2Key"])
    print("pubKeyHash :", zk_keys["pubKeyHash"])

    banner("register V3 account")
    nonce = client.generate_nonce_v3(
        refresh="false",
        l2Key=zk_keys["l2Key"],
        ethAddress=client.default_address,
        chainId=chain_id,
    )
    reg = client.register_user_v3(
        nonce=nonce["data"]["nonce"],
        l2Key=zk_keys["l2Key"],
        seeds=zk_keys["seeds"],
        ethereum_address=client.default_address,
    )
    api_key = reg["data"]["apiKey"]
    print("apiKey-key       :", api_key["key"])
    print("apiKey-secret    :", api_key["secret"])
    print("apiKey-passphrase:", api_key["passphrase"])

    banner("wait for backend to finalize, then refresh account")
    time.sleep(10)
    account = client.get_account_v3()

    banner("activate signing via change_pub_key_v3")
    spot = account.get("spotAccount") or {}
    change = client.change_pub_key_v3(
        chainId=chain_id,
        seeds=zk_keys["seeds"],
        ethPrivateKey=eth_private_key,
        zkAccountId=spot.get("zkAccountId"),
        subAccountId=spot.get("defaultSubAccountId"),
        newPkHash=zk_keys["pubKeyHash"],
        nonce=spot.get("nonce"),
        l2Key=zk_keys["l2Key"],
    )
    print("change_pub_key response:", change)

    banner("done — copy into .env")
    print("⚠  These values cannot be retrieved again. Store them now in your")
    print("   .env file (and a password manager). Avoid pasting into shared")
    print("   terminals, screenshots, chat logs, or CI output.")
    print()
    print(f"APEX_API_KEY={api_key['key']}")
    print(f"APEX_API_SECRET={api_key['secret']}")
    print(f"APEX_API_PASSPHRASE={api_key['passphrase']}")
    print(f"APEX_ZK_SEEDS={zk_keys['seeds']}")
    print(f"APEX_ZK_L2KEY={zk_keys['l2Key']}")


if __name__ == "__main__":
    main()
