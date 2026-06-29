"""
Multi-address registration — step 1.

Registers an LP account tied to a separate "mul" ethereum address. Save
the printed apiKey, zkKeys, accountId etc. into .env, then run step 2
(08_register_mul_address_step2.py) to activate it.

Prerequisites (in .env):
    ETH_PRIVATE_KEY            – primary ETH private key
    APEX_MUL_ETH_ADDRESS       – the secondary ETH address you want to bind

Run:
    python tests/07_register_mul_address_step1.py
"""
import time

from _common import banner, env_network, require
from apexomni.http_private_v3 import HttpPrivate_v3


def main():
    endpoint, network_id, chain_id = env_network()
    eth_private_key = require("ETH_PRIVATE_KEY")
    mul_address = require("APEX_MUL_ETH_ADDRESS")

    client = HttpPrivate_v3(endpoint, network_id=network_id, eth_private_key=eth_private_key)
    client.configs_v3()

    banner("derive ZK keys")
    zk = client.derive_zk_key(client.default_address)
    print(zk)

    banner("register LP account bound to mul address")
    nonce = client.generate_nonce_v3(
        refresh="false", l2Key=zk["l2Key"],
        ethAddress=client.default_address, chainId=chain_id,
    )
    reg = client.register_user_v3(
        nonce=nonce["data"]["nonce"],
        l2Key=zk["l2Key"], seeds=zk["seeds"],
        ethereum_address=client.default_address,
        eth_mul_address=mul_address,
        isLpAccount=True,
    )
    print(reg)

    banner("wait, then refresh account")
    time.sleep(10)
    account = client.get_account_v3()
    print(account)

    banner("save these into .env for step 2")
    print("⚠  These values cannot be retrieved again. Store them now in your")
    print("   .env file (and a password manager). Avoid pasting into shared")
    print("   terminals, screenshots, chat logs, or CI output.")
    print()
    api_key = reg["data"]["apiKey"]
    print(f"APEX_API_KEY={api_key['key']}")
    print(f"APEX_API_SECRET={api_key['secret']}")
    print(f"APEX_API_PASSPHRASE={api_key['passphrase']}")
    print(f"APEX_ZK_SEEDS={zk['seeds']}")
    print(f"APEX_ZK_L2KEY={zk['l2Key']}")
    print(f"APEX_ZK_PUBKEY_HASH={zk['pubKeyHash']}")


if __name__ == "__main__":
    main()
