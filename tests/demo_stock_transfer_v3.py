import sys

from apexomni.constants import APEX_OMNI_HTTP_TEST, NETWORKID_OMNI_TEST_BNB
from apexomni.helpers.request_helpers import random_client_id
from apexomni.http_private_sign import HttpPrivateStockSign

# Replace these with your own credentials/seeds before running the demo.
primary_credentials = {
    'key': 'your apiKey-key from register V3',
    'secret': 'our apiKey-secret from register  V3',
    'passphrase': 'your apiKey-passphrase from register  V3',
}
seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'

def main():
    print("Hello, Apex Omni stock transfer demo")
    client = HttpPrivateStockSign(
        APEX_OMNI_HTTP_TEST,
        network_id=NETWORKID_OMNI_TEST_BNB,
        zk_seeds=seeds,
        zk_l2Key=l2Key,
        api_key_credentials=primary_credentials,
    )

    # Cache configs and both account contexts.
    client.configs_v3()
    primary_account = client.get_account_v3(account_type="primary") or {}
    stock_account = client.get_account_v3_stock() or {}

    # Contract -> stock transfer (uses primary API identity; stock details pulled from cache).
    contract_to_stock = client.transfer_contract_to_stock_v3(
        amount="1",  # replace with the amount to transfer
        token="USDT",
        clientId=random_client_id(),
    )
    print("Contract -> stock transfer response:", contract_to_stock)

    # Stock -> contract transfer using the same /api/v3/contract-transfer-to
    # endpoint. Uses stock API identity; contract details pulled from primary cache.
    stock_to_contract = client.transfer_stock_to_contract_v3(
        amount="1",  # replace with the amount to transfer
        token="USDT",
        clientId=random_client_id(),
    )
    print("Stock -> contract transfer response:", stock_to_contract)

    print("end, Apex Omni stock transfer demo")


if __name__ == "__main__":
    sys.exit(main())
