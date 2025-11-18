import sys
import time

from apexomni.http_private_sign import HttpPrivateStockSign
from apexomni.constants import (
    APEX_OMNI_HTTP_TEST,
    NETWORKID_OMNI_TEST_BNB,
)
from apexomni.helpers.util import round_size


# Replace these with env vars; leave stock API blank to auto-generate via /stock/generate-api.
primary_credentials = {
    'key': 'your apiKey-key from register V3',
    'secret': 'our apiKey-secret from register  V3',
    'passphrase': 'your apiKey-passphrase from register  V3',
}
seeds = 'your zk seeds from register'
l2Key = 'your l2Key seeds from register'


def main():
    print("Hello, Apex Omni Stock - place order demo")
    client = HttpPrivateStockSign(
        APEX_OMNI_HTTP_TEST,
        network_id=NETWORKID_OMNI_TEST_BNB,
        zk_seeds=seeds,
        zk_l2Key=l2Key,
        api_key_credentials=primary_credentials,
    )

    # Primary account for eth address.
    primary_account = client.get_account_v3() or {}
    eth_address = primary_account.get('ethereumAddress')
    if not eth_address:
        raise RuntimeError("Missing primary ethereumAddress")

    # Fetch symbol config to respect tick/step sizing if available.
    configs = client.configs_v3()
    symbol = "AAPL-USDT"  # replace with an available stock symbol
    step_size = None
    tick_size = None
    for entry in configs.get('data', {}).get('symbolConfig', []):
        if entry.get('symbol') == symbol:
            step_size = entry.get('stepSize')
            tick_size = entry.get('tickSize')
            break

    # Example limit order
    raw_size = "0.01"
    raw_price = "150"
    size = round_size(raw_size, step_size) if step_size else raw_size
    price = round_size(raw_price, tick_size) if tick_size else raw_price
    client_order_id = f"demo-{int(time.time())}"

    order_res = client.create_order_v3(
        symbol=symbol,
        side="BUY",
        type="LIMIT",
        size=size,
        price=price,
        clientId=client_order_id,
        takerFeeRate="0.0005",
        makerFeeRate="0.0002",
        account_type = "stock"
    )
    print("Create stock order response:", order_res)

    # Example query order
    order = client.get_order_v3(id="781074154758603374")
    order = client.get_order_v3(clientOrderId="demo-1764064170")

    print(order)


if __name__ == "__main__":
    sys.exit(main())
