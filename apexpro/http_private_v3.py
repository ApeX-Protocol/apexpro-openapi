import hashlib
import json
import time

import zklink_sdk as sdk
from apexpro.constants import URL_SUFFIX, APEX_OMNI_HTTP_TEST
from apexpro.http_private import HttpPrivate


class HttpPrivate_v3(HttpPrivate):

    def generate_nonce_v3(self, l2Key, ethAddress, chainId,
                       refresh="false"
                       ):
        """"
        POST: Generate nonce.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-generate-nonce
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/generate-nonce"
        return self._private_request(
            method="POST",
            path=path,
            data={
                'l2Key': l2Key,
                'ethAddress': ethAddress,
                'chainId': chainId,
                'category': 'CATEGORY_API',
                'refresh': refresh,
            }
        )

    def register_user_v3(
            self,
            nonce,
            l2Key=None,
            seeds=None,
            ethereum_address=None,
            referred_by_affiliate_link=None,
            country=None,
            isLpAccount=None,
            eth_mul_address=None,
            sourceFlag=None,
    ):
        """"
        POST Registration & Onboarding.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-registration-amp-onboarding
        :returns: Request results as dictionary.
        """
        l2_key = l2Key or self.zk_l2Key
        l2_seeds = seeds or self.zk_seeds

        if l2_key is None:
            raise ValueError(
                'zk l2Key is required'
            )

        if l2_seeds is None:
            raise ValueError(
                'zk seeds is required'
            )

        eth_address = ethereum_address or self.default_address

        msg = str(l2_key.removeprefix('0x') + eth_address + nonce).lower()
        message = hashlib.sha256()
        message.update(msg.encode())  # Encode as UTF-8.
        msgHash = message.digest()


        EC_ORDER = '3618502788666131213697322783095070105526743751716087489154079457884512865583';

        bn1 = int(msgHash.hex(), 16)
        bn2 = int (EC_ORDER, 10)

        bn3 = hex(bn1)
        signMsg = hex(bn1.__mod__(bn2))

        seeds = bytes.fromhex(l2_seeds)
        signerSeed = sdk.ZkLinkSigner.new_from_seed(seeds)
        signatureOnboard = signerSeed.sign_musig(signMsg.removeprefix('0x').encode())

        apiKeyHash = hex(bn1).removeprefix('0x') + '|' + signMsg.removeprefix('0x')

        path = URL_SUFFIX + "/v3/onboarding"
        onboardingRes = self._private_request(
            method="POST",
            path=path,
            data= {
                'l2Key': l2_key,
                'referredByAffiliateLink': referred_by_affiliate_link,
                'ethereumAddress': eth_address,
                'country': country,
                'category': 'CATEGORY_API',
                'isLpAccount': isLpAccount,
                'ethMulAddress': eth_mul_address,
                'sourceFlag': sourceFlag,
                'apiKeyHash': apiKeyHash,
            },
            headers={
                'APEX-SIGNATURE': signatureOnboard.signature,
                'APEX-ETHEREUM-ADDRESS': eth_address,
            }
        )
        if onboardingRes.get('data') is not None:
            self.user = onboardingRes.get('data').get('user')
            self.accountV3 = onboardingRes.get('data').get('account')
            key = onboardingRes['data']['apiKey']['key']
            secret = onboardingRes['data']['apiKey']['secret']
            passphrase = onboardingRes['data']['apiKey']['passphrase']
            self.api_key_credentials = {'key': key,'secret': secret, 'passphrase': passphrase}
        return onboardingRes


    def derive_zk_key(
            self,
            ethereum_address=None,
    ):
        msgHeader = 'ApeX Omni Mainnet'
        if self.endpoint == APEX_OMNI_HTTP_TEST:
            msgHeader = 'ApeX Omni Testnet'
        signature = self.starkeySigner.sign_zk_message(
            ethereum_address or self.default_address,
            msgHeader,
            )

        seedstr = signature.removeprefix("0x")
        seeds = bytes.fromhex(seedstr)
        self.zk_seeds = seedstr
        signerSeed = sdk.ZkLinkSigner.new_from_seed(seeds)
        pubKey = signerSeed.public_key()
        self.zk_l2Key = pubKey
        pubKeyHash = sdk.get_public_key_hash(pubKey)

        return {
            'seeds': seedstr,
            'l2Key': pubKey,
            'pubKeyHash': pubKeyHash
        }

    def user_v3(self, **kwargs):
        """"
        GET Retrieve User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/user"
        userRes = self._get(
            endpoint=path,
            params=kwargs
        )
        self.user = userRes.get('data')
        return userRes

    def get_user_v3(self, **kwargs):
        """"
        GET Retrieve User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/user"
        userRes = self._get(
            endpoint=path,
            params=kwargs
        )
        self.user = userRes.get('data')
        return userRes


    def modify_user_v3(self, **kwargs):
        """"
        POST Edit User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-edit-user-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/modify-user"

        return self._post(
            endpoint=path,
            data=kwargs
        )


    def get_account_v3(self, **kwargs):
        """"
        GET Retrieve User Account Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-account-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/account"
        accountRes =  self._get(
            endpoint=path,
            params=kwargs
        )
        self.accountV3 = accountRes.get('data')
        self.default_address = self.accountV3.get('ethereumAddress')
        return accountRes.get('data')

    def transfers_v3(self, **kwargs):
        """"
        GET Retrieve User Deposit Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-deposit-data
        :returns: Request results as dictionary.
        """

        kwargs.update(subAccountId='0')
        path = URL_SUFFIX + "/v3/transfers"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def transfer_v3(self, **kwargs):
        """"
        GET Retrieve User Deposit Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-deposit-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/transfer"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def contract_transfers_v3(self, **kwargs):
        """"
        GET Retrieve User Deposit Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-deposit-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/contract-transfers"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def contract_transfer_v3(self, **kwargs):
        """"
        GET Retrieve User Deposit Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-deposit-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/contract-transfer"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def withdraw_list_v3(self, **kwargs):
        """"
        GET Retrieve User Withdrawal List.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-withdrawal-list
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/withdraw-list"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def contract_transfer_limit_v3(self, **kwargs):
        """"
        GET Retrieve Withdrawal & Transfer Limits.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-withdrawal-amp-transfer-limits
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/contract-transfer-limit"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def fills_v3(self, **kwargs):
        """"
        GET Retrieve Trade History.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-trade-history
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/fills"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def order_fills_v3(self, **kwargs):

        path = URL_SUFFIX + "/v3/order-fills"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def delete_order_v3(self, **kwargs):
        """"
        POST Cancel Order.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-cancel-order
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/delete-order"
        return self._post(
            endpoint=path,
            data=kwargs
        )


    def delete_order_by_client_order_id_v3(self, **kwargs):
        """"
        POST Cancel Order.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-cancel-order
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/delete-client-order-id"
        return self._post(
            endpoint=path,
            data=kwargs
        )

    def delete_open_orders_v3(self, **kwargs):
        """"
        POST Cancel all Open Orders
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-cancel-all-open-orders
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/delete-open-orders"
        return self._post(
            endpoint=path,
            data=kwargs
        )

    def open_orders_v3(self, **kwargs):
        """"
        GET Retrieve Open Orders.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-open-orders
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/open-orders"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def history_orders_v3(self, **kwargs):
        """"
        GET Retrieve All Order History.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-all-order-history
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/history-orders"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def get_order_v3(self, **kwargs):
        """"
        GET Retrieve Order ID.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-order-id
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/order"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def get_order_by_client_order_id_v3(self, **kwargs):
        """"
        GET Retrieve Order ID.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-order-id
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/order-by-client-id"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def funding_v3(self, **kwargs):
        """"
        GET Retrieve Funding Rate.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-funding-rate
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/funding"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def historical_pnl_v3(self, **kwargs):
        """"
        GET Retrieve User Historial Profit and Loss.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-historial-profit-and-loss
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/historical-pnl"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def yesterday_pnl_v3(self, **kwargs):
        """"
        GET Retrieve Yesterday's Profit & Loss.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-yesterday-39-s-profit-amp-loss
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/yesterday-pnl"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def history_value_v3(self, **kwargs):
        """"
        GET Retrieve Historical Asset Value.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-historical-asset-value
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/history-value"
        return self._get(
            endpoint=path,
            params=kwargs
        )


    def get_worst_price_v3(self, **kwargs):
        """"
        get market price from orderbook
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-worst-price
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/get-worst-price"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def get_order_by_client_id_v3(self, **kwargs):
        """"
        get market price from orderbook
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-worst-price
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/order-by-client-id"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def get_account_balance_v3(self, **kwargs):
        """"
        get market price from orderbook
        :param kwargs: See
        https://api-docs.pro.apex.exchange/?lang=zh-TW#privateapi-get-retrieve-user-account-balance
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/account-balance"
        return self._get(
            endpoint=path,
            params=kwargs
        )



    def set_initial_margin_rate_v3(self, **kwargs):
        """"
        get market price from orderbook
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-post-sets-the-initial-margin-rate-of-a-contract
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/set-initial-margin-rate"
        return self._post(
            endpoint=path,
            data=kwargs
        )


    def change_pub_key_v3(self,
                          chainId,
                          zkAccountId,
                          seeds,
                          newPkHash,
                          nonce,
                          l2Key,
                          feeToken=None,
                          asset='USDT',
                          subAccountId='0',
                          fee='0',
                          ethPrivateKey = None,
                          ethSignatureType='EthECDSA',
                          signature=None,
                          ethSignature=None,
                          timestamp=None,):
        path = URL_SUFFIX + "/v3/change-pub-key"

        times = timestamp or int(time.time())

        #signer1 = sdk.ZkLinkSigner().new_from_hex_eth_signer(ethPrivateKey)
        #pubKey = signer1.public_key()
        #newPkHash = sdk.get_public_key_hash(pubKey)

        feeToken = feeToken or self.configV3.get('spotConfig').get('global').get('defaultChangePubKeyFeeTokenId')

        builder = sdk.ChangePubKeyBuilder(chainId, int(zkAccountId), int(subAccountId), newPkHash, int(feeToken), fee, int(nonce), ethSignature, int(times))
        tx = sdk.ChangePubKey(builder)


        seedsByte = bytes.fromhex(seeds.removeprefix('0x') )
        signerSeed = sdk.ZkLinkSigner.new_from_seed(seedsByte)
        auth_data = signerSeed.sign_musig(tx.get_bytes())
        signature = auth_data.signature
        if  ethSignatureType != 'Onchain' and ethPrivateKey is not None:
            signer = sdk.Signer(ethPrivateKey, sdk.L1SignerType.ETH())
            authSigner = json.loads(signer.sign_change_pubkey_with_eth_ecdsa_auth(tx).tx)
            ethSignature = authSigner.get('ethAuthData').get('ethSignature')

        print(builder)
        print(signature)

        return self._post(
            endpoint=path,
            data={
                'chainId': chainId,
                'zkAccountId': zkAccountId,
                'subAccountId' : subAccountId,
                'newPkHash': newPkHash,
                'feeToken': feeToken,
                'nonce':nonce,
                'l2Key': l2Key,
                'fee': fee,
                'ethSignatureType': ethSignatureType,
                'signature': signature,
                'ethSignature': ethSignature,
                'timestamp':times
            }
        )

    def withdraw_fee_v3(self, **kwargs):
        """"
        GET Fast & Cross-Chain Withdrawal Fees.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-fast-amp-cross-chain-withdrawal-fees
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/withdraw-fee"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def all_apikeys_v3(self, **kwargs):

        path = URL_SUFFIX + "/v3/all-api-keys"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def apikey_bind_ip_v3(self, **kwargs):

        path = URL_SUFFIX + "/v3/bind-ip"
        return self._post(
            endpoint=path,
            data=kwargs
        )

    def delete_api_key_v3(self, **kwargs):

        path = URL_SUFFIX + "/v3/delete-api-key"
        return self._post(
            endpoint=path,
            data=kwargs
        )

    def generate_api_key_v3(self, nonce,
                            ips, remark
                            ):
        l2_key = self.zk_l2Key
        l2_seeds = self.zk_seeds

        if l2_key is None:
            raise ValueError(
                'zk l2Key is required'
            )

        if l2_seeds is None:
            raise ValueError(
                'zk seeds is required'
            )

        eth_address =  self.default_address

        msg = str(l2_key.removeprefix('0x') + eth_address + nonce).lower()
        message = hashlib.sha256()
        message.update(msg.encode())  # Encode as UTF-8.
        msgHash = message.digest()


        EC_ORDER = '3618502788666131213697322783095070105526743751716087489154079457884512865583';

        bn1 = int(msgHash.hex(), 16)
        bn2 = int (EC_ORDER, 10)

        bn3 = hex(bn1)
        signMsg = hex(bn1.__mod__(bn2))

        seeds = bytes.fromhex(l2_seeds)
        signerSeed = sdk.ZkLinkSigner.new_from_seed(seeds)
        signatureOnboard = signerSeed.sign_musig(signMsg.removeprefix('0x').encode())

        path = URL_SUFFIX + "/v3/generate-api-key"
        return self._post(
            endpoint=path,
            data={
                'signature':signatureOnboard.signature,
                'l2Key':l2_key,
                'ips':ips,
                'remark':remark,
            }
        )
