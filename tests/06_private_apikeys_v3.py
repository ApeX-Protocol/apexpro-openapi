"""
Manage API keys — list and generate additional credential sets.

Useful when you want a separate API key bound to specific IPs for a
server-side bot, leaving your primary key for development.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE
    APEX_ZK_SEEDS / APEX_ZK_L2KEY
    ETH_PRIVATE_KEY  (only needed to derive default_address for nonce gen)

Run:
    python tests/06_private_apikeys_v3.py
"""
from _common import banner, env_network, make_signing_client


def main():
    _, _, chain_id = env_network()
    client = make_signing_client()

    banner("get_user_v3")
    print(client.get_user_v3())

    banner("all_apikeys_v3 (before)")
    print(client.all_apikeys_v3())

    banner("generate a new API key (remark=demo, IPs=127.0.0.1)")
    nonce = client.generate_nonce_v3(
        refresh="true",
        l2Key=client.zk_l2Key,
        ethAddress=client.default_address,
        chainId=chain_id,
    )
    print(client.generate_api_key_v3(
        remark="demo",
        ips="127.0.0.1",
        nonce=nonce["data"]["nonce"],
    ))

    banner("all_apikeys_v3 (after)")
    print(client.all_apikeys_v3())


if __name__ == "__main__":
    main()
