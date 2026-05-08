
from apexomni.http_private_sign import HttpPrivateRwaSign
from apexomni.constants import (
    APEX_OMNI_HTTP_TEST, NETWORKID_OMNI_TEST_BNB,
)

print("Hello, Apex Omni RWA")

primary_credentials = {
    'key': 'your apiKey-key from register V3',
    'secret': 'our apiKey-secret from register  V3',
    'passphrase': 'your apiKey-passphrase from register  V3',
}
seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'

client = HttpPrivateRwaSign(
    APEX_OMNI_HTTP_TEST,
    network_id=NETWORKID_OMNI_TEST_BNB,
    zk_seeds=seeds,
    zk_l2Key=l2Key,
    api_key_credentials=primary_credentials,
)

# First register the RWA account (if not already registered).
register_res = client.register_rwa_account_v3()
print("Registered RWA account:", register_res)

# Generate/refresh a RWA-specific API credential set.
wallet_name = "pythonSdk"
primary_account = client.get_account_v3()
eth_address = (primary_account or {}).get('ethereumAddress')
generate_res = client.generate_rwa_api_v3(
    wallet_name=wallet_name,
    eth_address=eth_address,
)
print("Generated RWA API:", generate_res)

# After generation, the credentials are cached under the RWA account type.
rwa_account = client.get_account_v3_rwa() or {}
print("Loaded RWA account:", rwa_account.get('id'))

print("end, Apex Omni RWA")
