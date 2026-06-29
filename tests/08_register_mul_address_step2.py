"""
Multi-address registration — step 2.

Activates the LP account registered in step 1 by calling change_pub_key_v3
with `ethSignatureType="Onchain"` (the secondary address has to sign the
operation on-chain).

Prerequisites (in .env, from step 1 output):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE
    APEX_ZK_SEEDS / APEX_ZK_L2KEY / APEX_ZK_PUBKEY_HASH

Run:
    python tests/08_register_mul_address_step2.py
"""
import time

from _common import banner, env_network, make_client, require


def main():
    _, _, chain_id = env_network()
    client = make_client()

    seeds = require("APEX_ZK_SEEDS")
    l2_key = require("APEX_ZK_L2KEY")
    pub_key_hash = require("APEX_ZK_PUBKEY_HASH")

    account = client.accountV3
    spot = (account or {}).get("spotAccount") or {}

    banner("change_pub_key_v3 with Onchain signature")
    change = client.change_pub_key_v3(
        chainId=chain_id,
        seeds=seeds,
        zkAccountId=spot.get("zkAccountId"),
        subAccountId=spot.get("defaultSubAccountId"),
        newPkHash=pub_key_hash,
        nonce=spot.get("nonce"),
        l2Key=l2_key,
        ethSignatureType="Onchain",
    )
    print(change)

    banner("refresh account after activation")
    time.sleep(10)
    print(client.get_account_v3())


if __name__ == "__main__":
    main()
