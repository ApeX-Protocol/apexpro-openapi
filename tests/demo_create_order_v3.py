import os
import sys
import time

from apexpro.http_private_sign import HttpPrivateSign
import os
import sys
import time

from apexpro.http_private_sign import HttpPrivateSign

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apexpro")


key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'


client = HttpPrivateSign(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_TEST,
                          zk_seeds=seeds,zk_l2Key=l2Key,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()
accountData = client.get_account_v3()


currentTime = time.time()
createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="SELL",
                                        type="MARKET", size="0.001", timestampSeconds= currentTime,
                                        price="60000")
print(createOrderRes)


print("end, Apexpro")


