"""
RWA transfer demo — move balances between the contract and RWA accounts,
and (optionally) transfer out to an external address.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE   (primary)
    APEX_ZK_SEEDS / APEX_ZK_L2KEY
    APEX_RWA_API_KEY / APEX_RWA_API_SECRET / APEX_RWA_API_PASSPHRASE
    RECEIVER_*  (only if you want to run the transfer-to-address sample)

Run:
    python tests/11_rwa_transfer.py
"""
from _common import banner, make_rwa_signing_client, optional
from apexomni.helpers.request_helpers import random_client_id


def main():
    client = make_rwa_signing_client()
    client.get_account_v3_rwa()

    banner("contract → RWA (USDT, 1.0)")
    print(client.transfer_contract_to_rwa_v3(
        amount="1", token="USDT", clientId=random_client_id(),
    ))

    banner("RWA → contract (USDT, 1.0)")
    print(client.transfer_rwa_to_contract_v3(
        amount="1", token="USDT", clientId=random_client_id(),
    ))

    receiver = optional("RECEIVER_ETH_ADDRESS")
    account = optional("RECEIVER_ACCOUNT_ID")
    zk_id = optional("RECEIVER_ZK_ACCOUNT_ID")
    if receiver and account and zk_id:
        banner("transfer-out to external address")
        print(client.create_transfer_out_to_address_v3(
            amount="1", asset="USDT",
            receiverAddress=receiver,
            receiverAccountId=account,
            receiverZkAccountId=zk_id,
            receiverSubAccountId=0,
            clientId=random_client_id(),
        ))
    else:
        banner("transfer-out skipped — set RECEIVER_* env vars to enable")


if __name__ == "__main__":
    main()
