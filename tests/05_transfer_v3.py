"""
V3 transfers and withdrawals.

The examples below are commented out by default — uncomment the one you
want to try and run again. Each one is annotated with what it does and
when to use it.

Prerequisites (in .env):
    APEX_API_KEY / APEX_API_SECRET / APEX_API_PASSPHRASE
    APEX_ZK_SEEDS / APEX_ZK_L2KEY
    RECEIVER_ETH_ADDRESS / RECEIVER_ACCOUNT_ID  (only for transfer-to-address)

Run:
    python tests/05_transfer_v3.py
"""
from _common import banner, make_signing_client, optional


def main():
    client = make_signing_client()

    banner("Examples — uncomment the one you want")

    # 1. Fund account → contract account
    # print(client.create_transfer_out_v3(amount="3.4359738368", asset="USDT"))

    # 2. Contract account → fund account
    # print(client.create_contract_transfer_out_v3(amount="0.005", asset="ETH"))

    # 3. Query the fast/cross-chain withdrawal fee
    # print(client.withdraw_fee_v3(amount="3", chainIds="9", tokenId="60141"))

    # 4. Fast withdraw (lower-latency, higher fee — fetched from withdraw_fee_v3)
    # print(client.create_withdrawal_v3(amount="3", asset="USDT", toChainId=9, isFastWithdraw=True))

    # 5. Normal withdraw (uses withdraw_fee_v3.normalWithdrawFee)
    # print(client.create_withdrawal_v3(amount="3", asset="USDT", toChainId=9, isFastWithdraw=False))

    # 6. Contract transfer to another user — needs receiver info in .env
    receiver = optional("RECEIVER_ETH_ADDRESS")
    receiver_account = optional("RECEIVER_ACCOUNT_ID")
    if receiver and receiver_account:
        print("[ready] RECEIVER_ETH_ADDRESS and RECEIVER_ACCOUNT_ID are set")
        # print(client.create_contract_transfer_to_address_v3(
        #     amount="1.1", asset="USDT",
        #     receiverAddress=receiver, receiverAccountId=receiver_account,
        #     receiverL2Key="0x...",
        # ))


if __name__ == "__main__":
    main()
