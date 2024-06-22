import os
import sys
import time
from threading import Timer

from apexpro.http_private_v3 import HttpPrivate_v3

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.http_private import HttpPrivate
from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN, APEX_OMNI_HTTP_TEST, \
    APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB

print("Hello, Apex Omni")

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'
pubKeyHash = 'your l2Key seeds from pubKeyHash'


client = HttpPrivate_v3(APEX_OMNI_HTTP_MAIN, network_id=NETWORKID_OMNI_MAIN_ARB, api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()

accountRes = client.get_account_v3()
print(accountRes)

changeRes = client.change_pub_key_v3(chainId=NETWORKID_OMNI_MAIN_ARB, seeds= seeds, zkAccountId = accountRes.get('spotAccount').get('zkAccountId'), subAccountId = accountRes.get('spotAccount').get('defaultSubAccountId'),
                                     newPkHash=pubKeyHash,  nonce=accountRes.get('spotAccount').get('nonce'), l2Key= l2Key, ethSignatureType='Onchain')
print(changeRes)

time.sleep(10)
accountRes = client.get_account_v3()
print(accountRes)
print("end, Apexpro")

