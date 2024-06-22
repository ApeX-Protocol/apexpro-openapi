import decimal
import os
import sys
import time

from apexpro.helpers.util import round_size

from apexpro.http_private_sign import HttpPrivateSign
import os
import sys
import time

from apexpro.http_private_sign import HttpPrivateSign

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST

print("Hello, Apex omni")

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

# sample6
# Create a  TP/SL order
# first, Set a slippage to get an acceptable slPrice or tpPrice
#slippage is recommended to be greater than 0.1
# when buying, the price = price*(1 + slippage). when selling, the price = price*(1 - slippage)
slippage = decimal.Decimal("-0.1")
slPrice =  decimal.Decimal("58000") * (decimal.Decimal("1") + slippage)
tpPrice =  decimal.Decimal("79000") * (decimal.Decimal("1") - slippage)

createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="BUY",
                                     type="LIMIT", size="0.01",
                                     price="65000",
                                     isOpenTpslOrder=True,
                                     isSetOpenSl=True,
                                     slPrice=slPrice,
                                     slSide="SELL",
                                     slSize="0.01",
                                     slTriggerPrice="58000",
                                     isSetOpenTp=True,
                                     tpPrice=tpPrice,
                                     tpSide="SELL",
                                     tpSize="0.01",
                                     tpTriggerPrice="79000",
                                     )
print(createOrderRes)


print("end, Apexpro")


