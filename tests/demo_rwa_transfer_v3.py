import sys

from apexomni.constants import APEX_OMNI_HTTP_TEST, NETWORKID_OMNI_TEST_BNB
from apexomni.helpers.request_helpers import random_client_id
from apexomni.http_private_sign import HttpPrivateRwaSign

# Replace these with your own credentials/seeds before running the demo.
primary_credentials = {
    'key': 'your apiKey-key from register V3',
    'secret': 'our apiKey-secret from register  V3',
    'passphrase': 'your apiKey-passphrase from register  V3',
}
seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'

def main():
    print("Hello, Apex Omni RWA transfer demo")
    client = HttpPrivateRwaSign(
        APEX_OMNI_HTTP_TEST,
        network_id=NETWORKID_OMNI_TEST_BNB,
        zk_seeds=seeds,
        zk_l2Key=l2Key,
        api_key_credentials=primary_credentials,
    )

    # Cache configs and both account contexts.
    client.configs_v3()
    primary_account = client.get_account_v3(account_type="primary") or {}
    rwa_account = client.get_account_v3_rwa() or {}

    # Contract -> RWA transfer (uses primary API identity; RWA details pulled from cache).
    contract_to_rwa = client.transfer_contract_to_rwa_v3(
        amount="1",  # replace with the amount to transfer
        token="USDT",
        clientId=random_client_id(),
    )
    print("Contract -> RWA transfer response:", contract_to_rwa)

    # RWA -> contract transfer using the same /api/v3/contract-transfer-to
    # endpoint. Uses RWA API identity; contract details pulled from primary cache.
    rwa_to_contract = client.transfer_rwa_to_contract_v3(
        amount="1",  # replace with the amount to transfer
        token="USDT",
        clientId=random_client_id(),
    )
    print("RWA -> contract transfer response:", rwa_to_contract)

    print("end, Apex Omni RWA transfer demo")


if __name__ == "__main__":
    sys.exit(main())
