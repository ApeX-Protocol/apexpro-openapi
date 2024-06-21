import decimal
import hashlib
import time

import numpy as np

import zklink_sdk as sdk
from apexpro.constants import URL_SUFFIX, ORDER_SIDE_BUY
from apexpro.helpers.request_helpers import random_client_id
from apexpro.http_private_v3 import HttpPrivate_v3
from apexpro.starkex.order import DECIMAL_CONTEXT_ROUND_UP, DECIMAL_CONTEXT_ROUND_DOWN


class HttpPrivateSign(HttpPrivate_v3):
    def create_order_v3(self,
                     symbol,
                     side,
                     type,
                     size,
                     subAccountId=None,
                     takerFeeRate=None,
                     makerFeeRate=None,
                     price=None,
                     accountId=None,
                     timeInForce="GOOD_TIL_CANCEL",
                     reduceOnly=False,
                     triggerPrice=None,
                     triggerPriceType=None,
                     trailingPercent=None,
                     clientId=None,
                     timestampSeconds=None,
                     isPositionTpsl = False,
                     signature=None,
                     isOpenTpslOrder=False,
                     isSetOpenSl=False,
                     isSetOpenTp=False,
                     slClientId=None,
                     slPrice=None,
                     slSide=None,
                     slSize=None,
                     slTriggerPrice=None,
                     tpClientId=None,
                     tpPrice=None,
                     tpSide=None,
                     tpSize=None,
                     tpTriggerPrice=None,
                     sourceFlag=None,
                     brokerId=None,):
        """"
        POST  create_order.
        client.create_order(symbol="BTC-USDT", side="SELL",
                                           type="LIMIT", size="0.01",
                                           price="20000")

       :returns: Request results as dictionary.
       """
        price = str(price)
        size = str(size)
        clientId = clientId or random_client_id()

        accountId = accountId or self.accountV3.get('id')
        if not accountId:
            raise Exception(
                'No accountId provided' +
                'please call get_account_v3()'
            )

        if not self.configV3:
            raise Exception(
                'No config provided' +
                'please call configs_v3()'
            )
        symbolData = None
        currency = {}
        for k, v in enumerate(self.configV3.get('contractConfig').get('perpetualContract')):
            if v.get('symbol') == symbol or v.get('symbolDisplayName') == symbol:
                symbolData = v
        if symbolData is None:
            for k, v in enumerate(self.configV3.get('contractConfig').get('prelaunchContract')):
                if v.get('symbol') == symbol or v.get('symbolDisplayName') == symbol:
                    symbolData = v

        for k, v2 in enumerate(self.configV3.get('contractConfig').get('assets')):
            if v2.get('token') == symbolData.get('settleAssetId'):
                currency = v2

        if symbolData is not None :
            number = decimal.Decimal(price) / decimal.Decimal(symbolData.get('tickSize'))
            if number > int(number):
                raise Exception(
                    'the price must Multiple of tickSize'
                )

        if not self.zk_seeds:
            raise Exception(
                'No signature provided and client was not ' +
                'initialized with zk_seeds'
            )

        timestampSeconds = timestampSeconds or int(time.time())
        timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)


        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')
        takerFeeRate = takerFeeRate or self.accountV3.get('contractAccount').get('takerFeeRate')
        makerFeeRate = makerFeeRate or self.accountV3.get('contractAccount').get('makerFeeRate')

        message = hashlib.sha256()
        message.update(clientId.encode())  # Encode as UTF-8.
        nonceHash = message.hexdigest()
        nonceInt = int(nonceHash, 16)

        maxUint32 = np.iinfo(np.uint32).max
        maxUint64 = np.iinfo(np.uint64).max

        slotId = (nonceInt % maxUint64)/maxUint32
        nonce = nonceInt % maxUint32
        accountId = int(accountId, 10) % maxUint32


        priceStr = (decimal.Decimal(price) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)
        sizeStr = (decimal.Decimal(size) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)

        takerFeeRateStr =  (decimal.Decimal(takerFeeRate) * decimal.Decimal(10000)).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)
        makerFeeRateStr =  (decimal.Decimal(makerFeeRate) * decimal.Decimal(10000)).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)

        builder = sdk.ContractBuilder(
            int(accountId),  int(subAccountId), int(slotId), int(nonce),  int(symbolData.get('l2PairId')), sizeStr.__str__(), priceStr.__str__(), side == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
        )


        tx = sdk.Contract(builder)
        seedsByte = bytes.fromhex(self.zk_seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)
        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature


        if side == ORDER_SIDE_BUY:
            human_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                decimal.Decimal(size),
                decimal.Decimal(price)
            )
            fee = DECIMAL_CONTEXT_ROUND_UP.multiply(human_cost, decimal.Decimal(takerFeeRate))
        else:
            human_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                decimal.Decimal(size),
                decimal.Decimal(price)
            )
            fee = DECIMAL_CONTEXT_ROUND_DOWN.multiply(human_cost, decimal.Decimal(takerFeeRate))

        limit_fee_rounded = DECIMAL_CONTEXT_ROUND_UP.quantize(
            decimal.Decimal(fee),
            decimal.Decimal(currency.get('showStep')), )

        sl_limit_fee_rounded = None
        slSignature = None
        slTriggerPriceType = None
        slExpiration = None
        tp_limit_fee_rounded = None
        tpSignature = None
        tpTriggerPriceType = None
        tpExpiration = None

        if isOpenTpslOrder == True:
            if isSetOpenSl == True:
                slTriggerPriceType = triggerPriceType
                slExpiration = timestampSeconds
                slClientId = slClientId or random_client_id()

                slMessage = hashlib.sha256()
                slMessage.update(slClientId.encode())  # Encode as UTF-8.
                slNonceHash = slMessage.hexdigest()
                slNonceInt = int(slNonceHash, 16)

                slSlotId = (slNonceInt % maxUint64)/maxUint32
                slNonce = slNonceInt % maxUint32

                slPriceStr = (decimal.Decimal(slPrice) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)
                slSizeStr = (decimal.Decimal(slSize) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)

                slBuilder = sdk.ContractBuilder(
                    int(accountId),  int(subAccountId), int(slSlotId), int(slNonce),  int(symbolData.get('l2PairId')), slSizeStr.__str__(), slPriceStr.__str__(), slSide == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
                )

                slTx = sdk.Contract(slBuilder)
                sl_auth_data = signerSeed.sign_musig(slTx.get_bytes())
                slSignature = sl_auth_data.signature

                if slSide == ORDER_SIDE_BUY:
                    slHuman_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                    decimal.Decimal(slSize),
                    decimal.Decimal(slPrice)
                    )
                    slFee = DECIMAL_CONTEXT_ROUND_UP.multiply(slHuman_cost, decimal.Decimal(takerFeeRate))
                else:
                    slHuman_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                        decimal.Decimal(slSize),
                        decimal.Decimal(slPrice)
                    )
                    slFee = DECIMAL_CONTEXT_ROUND_DOWN.multiply(slHuman_cost, decimal.Decimal(takerFeeRate))

                sl_limit_fee_rounded = DECIMAL_CONTEXT_ROUND_UP.quantize(
                    decimal.Decimal(slFee),
                    decimal.Decimal(currency.get('showStep')), )

            if isSetOpenTp == True:
                tpTriggerPriceType = triggerPriceType
                tpExpiration = timestampSeconds
                tpClientId = tpClientId or random_client_id()

                tpMessage = hashlib.sha256()
                tpMessage.update(tpClientId.encode())  # Encode as UTF-8.
                tpNonceHash = tpMessage.hexdigest()
                tpNonceInt = int(tpNonceHash, 16)

                tpSlotId = (tpNonceInt % maxUint64)/maxUint32
                tpNonce = tpNonceInt % maxUint32

                tpPriceStr = (decimal.Decimal(tpPrice) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)
                tpSizeStr = (decimal.Decimal(tpSize) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)

                tpBuilder = sdk.ContractBuilder(
                    int(accountId),  int(subAccountId), int(tpSlotId), int(tpNonce),  int(symbolData.get('l2PairId')), tpSizeStr.__str__(), tpPriceStr.__str__(), tpSide == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
                )

                tpTx = sdk.Contract(tpBuilder)
                tp_auth_data = signerSeed.sign_musig(tpTx.get_bytes())
                tpSignature = tp_auth_data.signature

                if tpSide == ORDER_SIDE_BUY:
                    tpHuman_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                        decimal.Decimal(tpSize),
                        decimal.Decimal(tpPrice)
                    )
                    tpFee = DECIMAL_CONTEXT_ROUND_UP.multiply(tpHuman_cost, decimal.Decimal(takerFeeRate))
                else:
                    tpHuman_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                        decimal.Decimal(tpSize),
                        decimal.Decimal(tpPrice)
                    )
                    tpFee = DECIMAL_CONTEXT_ROUND_DOWN.multiply(tpHuman_cost, decimal.Decimal(takerFeeRate))

                tp_limit_fee_rounded = DECIMAL_CONTEXT_ROUND_UP.quantize(
                    decimal.Decimal(tpFee),
                    decimal.Decimal(currency.get('showStep')), )

        order = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': timeInForce,
            'size': size,
            'price': price,
            'limitFee': str(limit_fee_rounded),
            'expiration': timestampSeconds,
            'triggerPrice': triggerPrice,
            'triggerPriceType': triggerPriceType,
            'trailingPercent': trailingPercent,
            'clientId': clientId,
            'signature': signature,
            'reduceOnly': reduceOnly,
            'isPositionTpsl': isPositionTpsl,
            'isOpenTpslOrder': isOpenTpslOrder,
            'isSetOpenSl': isSetOpenSl,
            'isSetOpenTp': isSetOpenTp,
            'slClientOrderId': slClientId,
            'slPrice': slPrice,
            'slSide': slSide,
            'slSize': slSize,
            'slTriggerPrice': slTriggerPrice,
            'slTriggerPriceType': slTriggerPriceType,
            'slExpiration': slExpiration,
            'slLimitFee': str(sl_limit_fee_rounded),
            'slSignature': slSignature,
            'tpClientOrderId': tpClientId,
            'tpPrice': tpPrice,
            'tpSide': tpSide,
            'tpSize': tpSize,
            'tpTriggerPrice': tpTriggerPrice,
            'tpTriggerPriceType': tpTriggerPriceType,
            'tpExpiration': tpExpiration,
            'tpLimitFee': str(tp_limit_fee_rounded),
            'tpSignature': tpSignature,
            'sourceFlag': sourceFlag,
            'brokerId':brokerId,
        }

        path = URL_SUFFIX + "/v3/order"
        return self._post(
            endpoint=path,
            data=order
        )

    def create_withdrawal_v3(self,
                          amount,
                          toChainId,
                          asset,
                          nonce=None,
                          l2SourceTokenId=None,
                          l1TargetTokenId=None,
                          zkAccountId=None,
                          subAccountId=None,
                          fee='0',
                          clientId=None,
                          timestampSeconds=None,
                          ethAddress=None,
                          isFastWithdraw=False,
                          signature=None, ):

        clientId = clientId or random_client_id()
        if not self.zk_seeds:
            raise Exception(
                'No signature provided and client was not ' +
                'initialized with zk_seeds'
            )

        timestampSeconds =  int(timestampSeconds or int(time.time()))


        ethAddress = ethAddress or self.accountV3.get('ethereumAddress')

        zkAccountId = zkAccountId or self.accountV3.get('spotAccount').get('zkAccountId')

        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')

        nonce = nonce or self.accountV3.get('spotAccount').get('subAccounts')[0].get('nonce')

        l2Key = self.zk_l2Key or self.accountV3.get('l2Key')
        if not ethAddress:
            raise Exception(
                'No ethAddress provided' +
                'please call get_user()'
            )


        if not self.configV3:
            raise Exception(
                'No config provided' +
                'please call configs_v3()'
            )

        currency = {}

        for k, v in enumerate(self.configV3.get('spotConfig').get('assets')):
            if v.get('token') == asset:
                currency = v

        l2SourceTokenId = l2SourceTokenId or currency.get('tokenId')
        l1TargetTokenId = l1TargetTokenId or currency.get('tokenId')

        withdraw_fee_ratio = 0
        if isFastWithdraw == True:
            withdraw_fee_ratio = decimal.Decimal(fee) * decimal.Decimal(10000) / decimal.Decimal(amount)
            withdraw_fee_ratio = withdraw_fee_ratio.quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)
            fee = (withdraw_fee_ratio * decimal.Decimal(amount) / 10000).__str__()


        amountStr = (decimal.Decimal(amount) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)
        #feeStr = (decimal.Decimal(fee) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)

        builder = sdk.WithdrawBuilder(
            int(zkAccountId),  int(subAccountId), int(toChainId),ethAddress, int(l2SourceTokenId),
            int(l1TargetTokenId), amountStr.__str__(), None, '0', int(nonce),  int(withdraw_fee_ratio),  False, int(timestampSeconds)
        )
        tx = sdk.Withdraw(builder)
        seedsByte = bytes.fromhex(self.zk_seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)

        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature

        withdraw = {
            'amount': amount,
            'timestamp': int(timestampSeconds),
            'ethAddress': ethAddress,
            'clientWithdrawId': clientId,
            'signature': signature,
            'zkAccountId': zkAccountId,
            'subAccountId': subAccountId,
            'l2Key': l2Key,
            'fee': str(fee),
            'toChainId': toChainId,
            'l2SourceTokenId': l2SourceTokenId,
            'l1TargetTokenId': l1TargetTokenId,
            'isFastWithdraw': isFastWithdraw,
            'nonce': nonce,
        }

        path = URL_SUFFIX + "/v3/withdrawal"
        return self._post(
            endpoint=path,
            data=withdraw
        )

    def create_transfer_out_v3(self,
                             amount,
                             asset,
                             nonce=None,
                             tokenId=None,
                             zkAccountId=None,
                             subAccountId=None,
                             fee='0',
                             clientId=None,
                             timestampSeconds=None,
                             receiverAccountId=None,
                             receiverZkAccountId=None,
                             receiverSubAccountId=None,
                             receiverAddress=None,
                             signature=None, ):

        clientId = clientId or random_client_id()
        if not self.zk_seeds:
            raise Exception(
                'No signature provided and client was not ' +
                'initialized with zk_seeds'
            )

        timestampSeconds =  int(timestampSeconds or int(time.time()))
        zkAccountId = zkAccountId or self.accountV3.get('spotAccount').get('zkAccountId')
        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')
        nonce = nonce or self.accountV3.get('spotAccount').get('subAccounts')[0].get('nonce')

        receiverAddress = receiverAddress or self.configV3.get('spotConfig').get('global').get('contractAssetPoolEthAddress')
        receiverZkAccountId = receiverZkAccountId or self.configV3.get('spotConfig').get('global').get('contractAssetPoolZkAccountId')
        receiverSubAccountId = receiverSubAccountId or self.configV3.get('spotConfig').get('global').get('contractAssetPoolSubAccount')
        receiverAccountId = receiverAccountId or self.configV3.get('spotConfig').get('global').get('contractAssetPoolAccountId')

        if not self.configV3:
            raise Exception(
                'No config provided' +
                'please call configs_v3()'
            )

        currency = {}

        for k, v in enumerate(self.configV3.get('spotConfig').get('assets')):
            if v.get('token') == asset:
                currency = v

        tokenId = tokenId or currency.get('tokenId')

        amountStr = (decimal.Decimal(amount) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)

        builder = sdk.TransferBuilder(
            int(zkAccountId),  receiverAddress, int(subAccountId), int(receiverSubAccountId), int(tokenId), amountStr.__str__(), '0', int(nonce),  int(timestampSeconds)
        )

        tx = sdk.Transfer(builder)
        seedsByte = bytes.fromhex(self.zk_seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)

        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature

        transferData = {
            'amount': amount,
            'timestamp': int(timestampSeconds),
            'clientTransferId': clientId,
            'signature': signature,
            'zkAccountId': zkAccountId,
            'subAccountId': subAccountId,
            'fee': str(fee),
            'token': asset,
            'tokenId': tokenId,
            'receiverAccountId': receiverAccountId,
            'receiverZkAccountId': receiverZkAccountId,
            'receiverSubAccountId': receiverSubAccountId,
            'receiverAddress': receiverAddress,
            'nonce': nonce,
        }

        path = URL_SUFFIX + "/v3/transfer-out"
        return self._post(
            endpoint=path,
            data=transferData
        )

    def create_contract_transfer_out_v3(self,
                                        amount,
                                        asset,
                                        nonce=None,
                                        tokenId=None,
                                        zkAccountId=None,
                                        subAccountId=None,
                                        ethAddress=None,
                                        clientId=None,
                                        timestampSeconds=None,
                                        accountId=None,
                                        receiverAccountId=None,
                                        receiverZkAccountId=None,
                                        receiverSubAccountId=None,
                                        receiverAddress=None,
                                        signature=None, ):

        clientId = clientId or random_client_id()
        if not self.zk_seeds:
            raise Exception(
             'No signature provided and client was not ' +
             'initialized with zk_seeds'
            )

        timestampSeconds =  timestampSeconds or int(time.time())
        timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)
        accountId = accountId or self.accountV3.get('id')
        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')

        ethAddress = ethAddress or self.accountV3.get('ethereumAddress')

        receiverSubAccountId = receiverSubAccountId or 0

        message = hashlib.sha256()
        message.update(clientId.encode())  # Encode as UTF-8.
        nonceHash = message.hexdigest()
        nonceInt = int(nonceHash, 16)
        maxUint32 = np.iinfo(np.uint32).max


        nonce = nonceInt % maxUint32
        accountId = int(accountId, 10) % maxUint32

        if not self.configV3:
            raise Exception(
               'No config provided' +
               'please call configs_v3()'
            )

        currency = {}

        for k, v in enumerate(self.configV3.get('contractConfig').get('assets')):
            if v.get('token') == asset:
                currency = v

        tokenId = tokenId or currency.get('tokenId')

        amountStr = (decimal.Decimal(amount) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)

        builder = sdk.TransferBuilder(
            int(accountId),  ethAddress, int(subAccountId), int(receiverSubAccountId),  int(tokenId), amountStr.__str__(), '0', int(nonce),  int(timestampSeconds)
        )

        tx = sdk.Transfer(builder)
        seedsByte = bytes.fromhex(self.zk_seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)

        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature

        transferData = {
            'amount': amount,
            'expireTime': timestampSeconds,
            'clientWithdrawId': clientId,
            'signature': signature,
            'token': asset,
            'ethAddress': ethAddress,
        }

        path = URL_SUFFIX + "/v3/contract-transfer-out"
        return self._post(
            endpoint=path,
            data=transferData
        )

    def create_contract_transfer_to_address_v3(self,
                                        amount,
                                        asset,
                                        receiverL2Key,
                                        receiverAccountId,
                                        receiverAddress,
                                        receiverSubAccountId=None,
                                        nonce=None,
                                        tokenId=None,
                                        subAccountId=None,
                                        clientId=None,
                                        timestampSeconds=None,
                                        accountId=None,
                                        signature=None, ):

        clientId = clientId or random_client_id()
        if not self.zk_seeds:
            raise Exception(
                'No signature provided and client was not ' +
                'initialized with zk_seeds'
            )

        timestampSeconds =  timestampSeconds or int(time.time())
        timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)
        accountId = accountId or self.accountV3.get('id')
        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')
        receiverSubAccountId = receiverSubAccountId or 0

        message = hashlib.sha256()
        message.update(clientId.encode())  # Encode as UTF-8.
        nonceHash = message.hexdigest()
        nonceInt = int(nonceHash, 16)
        maxUint32 = np.iinfo(np.uint32).max


        nonce = nonceInt % maxUint32
        accountId = int(accountId, 10) % maxUint32

        if not self.configV3:
            raise Exception(
                'No config provided' +
                'please call configs_v3()'
            )

        currency = {}

        for k, v in enumerate(self.configV3.get('contractConfig').get('assets')):
            if v.get('token') == asset:
                currency = v

        tokenId = tokenId or currency.get('tokenId')

        amountStr = (decimal.Decimal(amount) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_UP)

        builder = sdk.TransferBuilder(
            int(accountId),  receiverAddress, int(subAccountId), int(receiverSubAccountId),  int(tokenId), amountStr.__str__(), '0', int(nonce),  int(timestampSeconds)
        )

        tx = sdk.Transfer(builder)
        seedsByte = bytes.fromhex(self.zk_seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)

        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature

        transferData = {
            'amount': amount,
            'expireTime': timestampSeconds,
            'clientTransferId': clientId,
            'signature': signature,
            'token': asset,
            'receiverAccountId': receiverAccountId,
            'receiverL2Key': receiverL2Key,
        }

        path = URL_SUFFIX + "/v3/contract-transfer-to"
        return self._post(
            endpoint=path,
            data=transferData
        )
