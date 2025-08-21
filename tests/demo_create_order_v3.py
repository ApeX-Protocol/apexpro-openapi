import decimal
import os
import sys
import time

from apexomni.helpers.util import round_size

from apexomni.http_private_sign import HttpPrivateSign
import os
import sys
import time

from apexomni.http_private_sign import HttpPrivateSign

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexomni.constants import NETWORKID_TEST, APEX_OMNI_HTTP_TEST, APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB, \
    NETWORKID_OMNI_TEST_BNB

print("Hello, Apex omni")

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'


client = HttpPrivateSign(APEX_OMNI_HTTP_TEST, network_id=NETWORKID_OMNI_TEST_BNB,
                         zk_seeds=seeds,zk_l2Key=l2Key,
                         api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs_v3()
accountData = client.get_account_v3()

currentTime = time.time()

# sample1
# When create an order, optimize the size of the order according to the stepSize of the currency symbol,
# and optimize the price of the order according to the tickSize
# can get positions data from account
symbolData = {}
for k, v in enumerate(configs.get('data').get('contractConfig').get('perpetualContract')):
    if v.get('symbol') == "BTC-USDT":
        symbolData = v

print(round_size("0.0116", symbolData.get('stepSize')))
print(round_size("125555.8", symbolData.get('tickSize')))

positions = accountData.get('positions')
print(positions)

# sample2
# Create a limit order
size = round_size("0.01", symbolData.get('stepSize'))
price = round_size("128888.5", symbolData.get('tickSize'))
createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="BUY",price=price,
                                     type="LIMIT", size=size)
print(createOrderRes)

# sample3
# Create a conditional order
createOrderRes = client.create_order_v3(symbol="ETH-USDT", side="BUY",price='2000',
                                     type="STOP_LIMIT", size="0.01",triggerPriceType="INDEX", triggerPrice="1811")
print(createOrderRes)

# sample4
# Create a market order
# also need a marketPrice, it is worse than the index price
marketPrice = round_size("108888.5", symbolData.get('tickSize'))

createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="SELL",
                                     type="MARKET", size="0.01", price=marketPrice)
print(createOrderRes)

# sample5
# Create a Position TP/SL order
# first, Set a slippage to get an acceptable price
# if timeInForce="GOOD_TIL_CANCEL" or "POST_ONLY", slippage is recommended to be greater than 0.1
# if timeInForce="FILL_OR_KILL" or "IMMEDIATE_OR_CANCEL", slippage is recommended to be greater than 0.2
# when buying, the price = price*(1 + slippage). when selling, the price = price*(1 - slippage)

createOrderRes = client.create_order_v3(symbol="BTC-USDT", side="BUY",size="0.02",
                                        price="110000",
                                        isPositionTpsl=True,
                                        reduceOnly=True,
                                        triggerPrice="100000",
                                        triggerPriceType="INDEX",
                                        type="TAKE_PROFIT_MARKET",
                                        )
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


print("end, Apex Omni")


