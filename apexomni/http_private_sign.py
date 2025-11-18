import decimal
import hashlib
import time

import numpy as np
import json

from apexomni import zklink_sdk as sdk
from apexomni.constants import URL_SUFFIX, ORDER_SIDE_BUY
from apexomni.helpers.request_helpers import random_client_id
from apexomni.http_private_v3 import HttpPrivate_v3, HttpPrivateStock_v3
from apexomni.starkex.order import DECIMAL_CONTEXT_ROUND_UP, DECIMAL_CONTEXT_ROUND_DOWN


class HttpPrivateSign(HttpPrivate_v3):
    def _get_account_snapshot(self, account_type=None):
        if hasattr(self, "_get_account_context"):
            return self._get_account_context(account_type)
        return getattr(self, "accountV3", None)

    def _resolve_signing_seeds(self, account_type=None):
        """
        Choose signing seeds based on the current account type.
        Prefers cached stock seeds when signing under the stock account.
        """
        account_type = account_type or getattr(self, "_default_account_type", "primary")
        if account_type == getattr(self, "stock_account_type", None):
            seeds = getattr(self, "stock_zk_seeds", None) or self.zk_seeds
            if seeds:
                return seeds
        return self.zk_seeds

    def _ensure_account_snapshot(self, account_type=None):
        account = self._get_account_snapshot(account_type)
        if not account:
            raise Exception(
                'No account data cached, please call get_account_v3()'
            )
        return account

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
                     brokerId=None,
                     account_type=None,):
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

        active_account_type = account_type or getattr(self, "_default_account_type", "primary")
        account = self._ensure_account_snapshot(active_account_type)

        accountId = accountId or account.get('id')
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

        if symbolData is None:
            for k, v in enumerate(self.configV3.get('contractConfig').get('predictionContract')):
                if v.get('symbol') == symbol or v.get('symbolDisplayName') == symbol:
                    symbolData = v
        if symbolData is None:
            for k, v in enumerate(self.configV3.get('contractConfig').get('stockContract')):
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

        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
            )

        timestampSeconds = timestampSeconds or int(time.time())
        timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)


        subAccountId = 0
        takerFeeRate = takerFeeRate or account.get('contractAccount').get('takerFeeRate')
        makerFeeRate = makerFeeRate or account.get('contractAccount').get('makerFeeRate')

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
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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
            decimal.Decimal("0.000001"), )

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
                slPrice = str(slPrice)
                slSize = str(slSize)
                slTriggerPriceType = triggerPriceType
                slExpiration = timestampSeconds * 1000
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
                    decimal.Decimal("0.000001"), )

            if isSetOpenTp == True:
                tpPrice = str(tpPrice)
                tpSize = str(tpSize)
                tpTriggerPriceType = triggerPriceType
                tpExpiration = timestampSeconds * 1000
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
                    decimal.Decimal("0.000001"), )

        order = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': timeInForce,
            'size': size,
            'price': price,
            'limitFee': str(limit_fee_rounded),
            'expiration': timestampSeconds * 1000,
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
            data=order,
            account_type=account_type,
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
        active_account_type = getattr(self, "_default_account_type", "primary")
        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
            )

        timestampSeconds =  int(timestampSeconds or int(time.time()))


        account = self._ensure_account_snapshot(account_type=None)
        ethAddress = ethAddress or account.get('ethereumAddress')

        zkAccountId = zkAccountId or account.get('spotAccount').get('zkAccountId')

        subAccountId = subAccountId or account.get('spotAccount').get('defaultSubAccountId')

        nonce = nonce or account.get('spotAccount').get('subAccounts')[0].get('nonce')

        l2Key = self.zk_l2Key or account.get('l2Key')
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
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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
        active_account_type = getattr(self, "_default_account_type", "primary")
        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
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
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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

    def create_transfer_out_to_address_v3(self,
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
        active_account_type = getattr(self, "_default_account_type", "primary")
        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
            )

        timestampSeconds =  int(timestampSeconds or int(time.time()))
        zkAccountId = zkAccountId or self.accountV3.get('spotAccount').get('zkAccountId')
        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')
        nonce = nonce or self.accountV3.get('spotAccount').get('subAccounts')[0].get('nonce')

        receiverSubAccountId = receiverSubAccountId or 0

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
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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

        path = URL_SUFFIX + "/v3/transfer-out-to-address"
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
        active_account_type = getattr(self, "_default_account_type", "primary")
        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
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
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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
        subAccountId = subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId') or 0
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
        signing_seeds = self._resolve_signing_seeds(account_type=getattr(self, "_default_account_type", "primary"))
        if signing_seeds is None:
            raise Exception('No signing seeds available for contract transfer')
        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
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

    def create_manual_repayment_v3(self,
                                   repaymentTokens,
                                   poolRepaymentTokens,
                                   clientId=None,
                                   timestampSeconds=None,
                                   accountId=None,
                                   signature=None, ):

        clientId = clientId or random_client_id()
        active_account_type = getattr(self, "_default_account_type", "primary")
        signing_seeds = self._resolve_signing_seeds(active_account_type)
        if not signing_seeds:
            raise Exception(
                'No signing seeds provided; set seeds for the active account type'
            )

        timestampSeconds =  timestampSeconds or int(time.time())
        timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)
        accountId = accountId or self.accountV3.get('id')

        msgHashString ="accountId=" + accountId + "&clientId=" + clientId + "&expireTime=" + str(timestampSeconds) + "&repaymentTokens=" + repaymentTokens

        message = hashlib.sha256()
        message.update(msgHashString.encode())  # Encode as UTF-8.
        msgHash = message.digest()

        EC_ORDER = '3618502788666131213697322783095070105526743751716087489154079457884512865583';

        bn1 = int(msgHash.hex(), 16)
        bn2 = int (EC_ORDER, 10)
        signMsg = hex(bn1.__mod__(bn2))

        seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)
        signatureData = signerSeed.sign_musig(signMsg.removeprefix('0x').encode())
        signature = signatureData.signature

        repaymentData = {
            'repaymentTokens': repaymentTokens,
            'expireTime': timestampSeconds,
            'clientId': clientId,
            'signature': signature,
            'poolRepaymentTokens': poolRepaymentTokens,
        }

        path = URL_SUFFIX + "/v3/manual-create-repayment"
        return self._post(
            endpoint=path,
            data=repaymentData
        )

    def create_batch_orders_v3(self, orders):
        createOrders = []
        for orderModel in orders:
            price = str(orderModel.price)
            size = str(orderModel.size)
            clientId = orderModel.clientId or random_client_id()

            accountId = orderModel.accountId or self.accountV3.get('id')
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
                if v.get('symbol') == orderModel.symbol or v.get('symbolDisplayName') == orderModel.symbol:
                    symbolData = v
            if symbolData is None:
                for k, v in enumerate(self.configV3.get('contractConfig').get('prelaunchContract')):
                    if v.get('symbol') == orderModel.symbol or v.get('symbolDisplayName') == orderModel.symbol:
                        symbolData = v
            if symbolData is None:
                for k, v in enumerate(self.configV3.get('contractConfig').get('predictionContract')):
                    if v.get('symbol') == orderModel.symbol or v.get('symbolDisplayName') == orderModel.symbol:
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

            active_account_type = getattr(self, "_default_account_type", "primary")
            signing_seeds = self._resolve_signing_seeds(active_account_type)
            if not signing_seeds:
                raise Exception(
                    'No signing seeds provided; set seeds for the active account type'
                )

            timestampSeconds = orderModel.timestampSeconds or int(time.time())
            timestampSeconds = int(timestampSeconds + 3600 * 24 * 28)


            subAccountId = orderModel.subAccountId or self.accountV3.get('spotAccount').get('defaultSubAccountId')
            takerFeeRate = orderModel.takerFeeRate or self.accountV3.get('contractAccount').get('takerFeeRate')
            makerFeeRate = orderModel.makerFeeRate or self.accountV3.get('contractAccount').get('makerFeeRate')

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
                int(accountId),  int(subAccountId), int(slotId), int(nonce),  int(symbolData.get('l2PairId')), sizeStr.__str__(), priceStr.__str__(), orderModel.side == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
            )


            tx = sdk.Contract(builder)
            seedsByte = bytes.fromhex(str(signing_seeds).removeprefix('0x') )
            signerSeed = sdk.ZkLinkSigner().new_from_seed(seedsByte)
            auth_data = signerSeed.sign_musig(tx.get_bytes())
            signature = auth_data.signature


            if orderModel.side == ORDER_SIDE_BUY:
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
                decimal.Decimal("0.000001"), )

            sl_limit_fee_rounded = None
            slSignature = None
            slTriggerPriceType = None
            slExpiration = None
            tp_limit_fee_rounded = None
            tpSignature = None
            tpTriggerPriceType = None
            tpExpiration = None

            if orderModel.isOpenTpslOrder == True:
                if orderModel.isSetOpenSl == True:
                    slTriggerPriceType = orderModel.triggerPriceType
                    slExpiration = timestampSeconds * 1000
                    slClientId = orderModel.slClientId or random_client_id()

                    slMessage = hashlib.sha256()
                    slMessage.update(slClientId.encode())  # Encode as UTF-8.
                    slNonceHash = slMessage.hexdigest()
                    slNonceInt = int(slNonceHash, 16)

                    slSlotId = (slNonceInt % maxUint64)/maxUint32
                    slNonce = slNonceInt % maxUint32

                    slPriceStr = (decimal.Decimal(str(orderModel.slPrice)) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)
                    slSizeStr = (decimal.Decimal(str(orderModel.slSize)) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)

                    slBuilder = sdk.ContractBuilder(
                        int(accountId),  int(subAccountId), int(slSlotId), int(slNonce),  int(symbolData.get('l2PairId')), slSizeStr.__str__(), slPriceStr.__str__(), slSide == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
                    )

                    slTx = sdk.Contract(slBuilder)
                    sl_auth_data = signerSeed.sign_musig(slTx.get_bytes())
                    slSignature = sl_auth_data.signature

                    if orderModel.slSide == ORDER_SIDE_BUY:
                        slHuman_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                            decimal.Decimal(str(orderModel.slSize)),
                            decimal.Decimal(str(orderModel.slPrice))
                        )
                        slFee = DECIMAL_CONTEXT_ROUND_UP.multiply(slHuman_cost, decimal.Decimal(takerFeeRate))
                    else:
                        slHuman_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                            decimal.Decimal(str(orderModel.slSize)),
                            decimal.Decimal(str(orderModel.slPrice))
                        )
                        slFee = DECIMAL_CONTEXT_ROUND_DOWN.multiply(slHuman_cost, decimal.Decimal(takerFeeRate))

                    sl_limit_fee_rounded = DECIMAL_CONTEXT_ROUND_UP.quantize(
                        decimal.Decimal(slFee),
                        decimal.Decimal("0.000001"), )

                if orderModel.isSetOpenTp == True:
                    tpTriggerPriceType = orderModel.triggerPriceType
                    tpExpiration = timestampSeconds * 1000
                    tpClientId = orderModel.tpClientId or random_client_id()

                    tpMessage = hashlib.sha256()
                    tpMessage.update(tpClientId.encode())  # Encode as UTF-8.
                    tpNonceHash = tpMessage.hexdigest()
                    tpNonceInt = int(tpNonceHash, 16)

                    tpSlotId = (tpNonceInt % maxUint64)/maxUint32
                    tpNonce = tpNonceInt % maxUint32

                    tpPriceStr = (decimal.Decimal(str(orderModel.tpPrice)) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)
                    tpSizeStr = (decimal.Decimal(str(orderModel.tpSize)) * decimal.Decimal(10) ** decimal.Decimal(currency.get('decimals'))).quantize(decimal.Decimal(0), rounding=decimal.ROUND_DOWN)

                    tpBuilder = sdk.ContractBuilder(
                        int(accountId),  int(subAccountId), int(tpSlotId), int(tpNonce),  int(symbolData.get('l2PairId')), tpSizeStr.__str__(), tpPriceStr.__str__(), tpSide == "BUY",  int(takerFeeRateStr), int(makerFeeRateStr),  False
                    )

                    tpTx = sdk.Contract(tpBuilder)
                    tp_auth_data = signerSeed.sign_musig(tpTx.get_bytes())
                    tpSignature = tp_auth_data.signature

                    if orderModel.tpSide == ORDER_SIDE_BUY:
                        tpHuman_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                            decimal.Decimal(str(orderModel.tpSize)),
                            decimal.Decimal(str(orderModel.tpPrice))
                        )
                        tpFee = DECIMAL_CONTEXT_ROUND_UP.multiply(tpHuman_cost, decimal.Decimal(takerFeeRate))
                    else:
                        tpHuman_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                            decimal.Decimal(str(orderModel.tpSize)),
                            decimal.Decimal(str(orderModel.tpPrice))
                        )
                        tpFee = DECIMAL_CONTEXT_ROUND_DOWN.multiply(tpHuman_cost, decimal.Decimal(takerFeeRate))

                    tp_limit_fee_rounded = DECIMAL_CONTEXT_ROUND_UP.quantize(
                        decimal.Decimal(tpFee),
                        decimal.Decimal("0.000001"), )

            order = {
                'symbol': orderModel.symbol,
                'side': orderModel.side,
                'type': orderModel.type,
                'timeInForce': orderModel.timeInForce,
                'size': size,
                'price': price,
                'limitFee': str(limit_fee_rounded),
                'expiration': timestampSeconds * 1000,
                'triggerPrice': orderModel.triggerPrice,
                'triggerPriceType': orderModel.triggerPriceType,
                'trailingPercent': orderModel.trailingPercent,
                'clientId': clientId,
                'signature': signature,
                'reduceOnly': orderModel.reduceOnly,
                'isPositionTpsl': orderModel.isPositionTpsl,
                'isOpenTpslOrder': orderModel.isOpenTpslOrder,
                'isSetOpenSl': orderModel.isSetOpenSl,
                'isSetOpenTp': orderModel.isSetOpenTp,
                'slClientOrderId': orderModel.slClientId,
                'slPrice': orderModel.slPrice,
                'slSide': orderModel.slSide,
                'slSize': orderModel.slSize,
                'slTriggerPrice': orderModel.slTriggerPrice,
                'slTriggerPriceType': slTriggerPriceType,
                'slExpiration': slExpiration,
                'slLimitFee': str(sl_limit_fee_rounded),
                'slSignature': slSignature,
                'tpClientOrderId': orderModel.tpClientId,
                'tpPrice': orderModel.tpPrice,
                'tpSide': orderModel.tpSide,
                'tpSize': orderModel.tpSize,
                'tpTriggerPrice': orderModel.tpTriggerPrice,
                'tpTriggerPriceType': tpTriggerPriceType,
                'tpExpiration': tpExpiration,
                'tpLimitFee': str(tp_limit_fee_rounded),
                'tpSignature': tpSignature,
                'sourceFlag': orderModel.sourceFlag,
                'brokerId':orderModel.brokerId,
            }
            createOrders.append(order)
        path = URL_SUFFIX + "/v3/batch-orders"
        return self._post(
            endpoint=path,
            data= {'orders':json.dumps(createOrders)}
        )


class HttpPrivateStockSign(HttpPrivateStock_v3, HttpPrivateSign):
    """
    Convenience client whose default signing context targets the stock account.
    """

    def __init__(self, *args, stock_prefix=None, **kwargs):
        super().__init__(*args, stock_prefix=stock_prefix, **kwargs)
        # Auto-register stock account and cache stock API credentials if missing.
        try:
            # Register stock account (idempotent on server).
            self.register_stock_account_v3()
            creds = self._get_api_credentials(self.stock_account_type)
            if not creds:
                stock_account = self.get_account_v3_stock() or {}
                account_id = stock_account.get('stockAccountId') or stock_account.get('id')
                primary_account = self.get_account_v3() or {}
                eth_address = primary_account.get('ethereumAddress')
                chain_id = getattr(self, "network_id", None)
                self.generate_stock_api_v3(
                    wallet_name="Auto Stock Wallet",
                    account_id=account_id,
                    eth_address=eth_address,
                    chain_id=chain_id,
                )
        except Exception:
            # Do not block client construction if auto-generation fails.
            pass

    def use_primary_account(self):
        """
        Switch signing back to the primary V3 account.
        """
        self.set_default_account_type("primary")
        primary_credentials = self._get_api_credentials("primary")
        if primary_credentials:
            self.api_key_credentials = primary_credentials

    def transfer_contract_to_stock_v3(
            self,
            amount,
            token,
            clientId=None,
            timestampSeconds=None,
    ):
        """
        Convenience wrapper for contract -> stock transfer using primary API identity.
        Only amount/token are required; stock receiver info comes from cached stock account.
        """
        if not self.configV3:
            self.configs_v3()
        previous_account_type = getattr(self, "_default_account_type", "primary")
        self.use_primary_account()
        try:
            primary_account = self.get_account_v3(account_type="primary") or {}
            stock_account = self.get_account_v3_stock() or {}
            receiver_account_id = stock_account.get('stockAccountId') or stock_account.get('id')
            receiver_l2_key = (
                stock_account.get('l2Key')
                or stock_account.get('omniSwapAccount', {}).get('l2Key')
            )
            receiver_address = stock_account.get('ethereumAddress') or primary_account.get('ethereumAddress')
            if not receiver_account_id or not receiver_l2_key or not receiver_address:
                raise ValueError('Stock account context is missing receiver details')
            return self.create_contract_transfer_to_address_v3(
                amount=amount,
                asset=token,
                receiverAccountId=receiver_account_id,
                receiverL2Key=receiver_l2_key,
                receiverAddress=receiver_address,
                clientId=clientId,
                timestampSeconds=timestampSeconds,
            )
        finally:
            self.set_default_account_type(previous_account_type)

    def transfer_stock_to_contract_v3(
            self,
            amount,
            token,
            clientId=None,
            timestampSeconds=None,
    ):
        """
        Convenience wrapper for stock -> contract transfer using stock API identity.
        Only amount/token are required; contract receiver info comes from cached primary account.
        """
        if not self.configV3:
            self.configs_v3()
        previous_account_type = getattr(self, "_default_account_type", "primary")
        self.set_default_account_type(self.stock_account_type)
        stock_credentials = self._get_api_credentials(self.stock_account_type)
        if stock_credentials:
            self.api_key_credentials = stock_credentials
        # Ensure signing context uses stock account snapshot.
        stock_account = self.get_account_v3_stock() or {}
        current_account_ctx = getattr(self, "accountV3", None)
        if stock_account:
            self._set_account_context(stock_account, account_type=self.stock_account_type)
            self.accountV3 = stock_account
        stock_account_id = stock_account.get('stockAccountId') or stock_account.get('id')
        try:
            primary_account = self.get_account_v3(account_type="primary") or {}
            contract_receiver_id = primary_account.get('id')
            contract_receiver_l2_key = (
                primary_account.get('l2Key')
                or primary_account.get('contractAccount', {}).get('l2Key')
            )
            contract_receiver_address = primary_account.get('ethereumAddress')
            if not contract_receiver_id or not contract_receiver_l2_key or not contract_receiver_address:
                raise ValueError('Primary account context is missing receiver details')
            return self.create_contract_transfer_to_address_v3(
                amount=amount,
                asset=token,
                receiverAccountId=contract_receiver_id,
                receiverL2Key=contract_receiver_l2_key,
                receiverAddress=contract_receiver_address,
                clientId=clientId,
                timestampSeconds=timestampSeconds,
                accountId=stock_account_id,
            )
        finally:
            # Restore previous account context.
            if current_account_ctx is not None:
                self.accountV3 = current_account_ctx
            self.set_default_account_type(previous_account_type)
