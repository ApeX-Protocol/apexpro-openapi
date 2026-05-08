import hashlib
import json
import time
import urllib

from eth_account import Account
from mnemonic import Mnemonic

from apexomni import zklink_sdk as sdk
from apexomni.constants import URL_SUFFIX, APEX_OMNI_HTTP_TEST
from apexomni.helpers.request_helpers import random_client_id
from apexomni.http_private import HttpPrivate


class HttpPrivate_v3(HttpPrivate):

    def _set_account_context(self, account_data, account_type="primary"):
        if not hasattr(self, "_account_context"):
            self._account_context = {}
        if account_data is not None:
            self._account_context[account_type] = account_data
            default_type = getattr(self, "_default_account_type", "primary")
            if account_type == default_type:
                self.accountV3 = account_data
            elif account_type == "primary" and default_type == "primary":
                self.accountV3 = account_data
        return account_data

    def _get_account_context(self, account_type=None):
        account_type = account_type or getattr(self, "_default_account_type", "primary")
        context = getattr(self, "_account_context", {})
        if context:
            if account_type in context:
                return context[account_type]
            return context.get("primary")
        return getattr(self, "accountV3", None)

    def set_default_account_type(self, account_type):
        self._default_account_type = account_type
        account = self._get_account_context(account_type)
        if account is not None:
            self.accountV3 = account

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

        path = URL_SUFFIX + "/v3/new-onboarding"
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
            self._set_account_context(onboardingRes.get('data').get('account'), account_type="primary")
            key = onboardingRes['data']['apiKey']['key']
            secret = onboardingRes['data']['apiKey']['secret']
            passphrase = onboardingRes['data']['apiKey']['passphrase']
            self._set_api_key_credentials(
                {'key': key, 'secret': secret, 'passphrase': passphrase},
                account_type="primary",
            )
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


    def get_account_v3(self, account_type="primary", **kwargs):
        """"
        GET Retrieve User Account Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-account-data
        :returns: Request results as dictionary.
        """

        path = URL_SUFFIX + "/v3/account"
        accountRes =  self._get(
            endpoint=path,
            params=kwargs,
            account_type=account_type,
        )
        if accountRes.get('data') is not None:
            account_data = self._set_account_context(accountRes.get('data'), account_type=account_type)
            if account_data and account_type == "primary":
                self.default_address = account_data.get('ethereumAddress')
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


class HttpPrivateRwa_v3(HttpPrivate_v3):
    """
    Specialized V3 client for RWA sub-accounts.
    Reuses core V3 flows but signs requests with the RWA API key set.
    """

    RWA_ACCOUNT_TYPE = "rwa"
    DEFAULT_RWA_PREFIX = URL_SUFFIX + "/v3/stock"

    def __init__(self, *args, rwa_prefix=None, default_to_rwa=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.rwa_account_type = self.RWA_ACCOUNT_TYPE
        self.rwa_prefix = rwa_prefix or self.DEFAULT_RWA_PREFIX
        if default_to_rwa:
            self.set_default_account_type(self.rwa_account_type)

    def set_rwa_api_credentials(self, credentials):
        """
        Register API key credentials for the RWA account.
        """
        self._set_api_key_credentials(credentials, account_type=self.rwa_account_type)
        if getattr(self, "_default_account_type", "primary") == self.rwa_account_type:
            self.api_key_credentials = credentials

    def _rwa_path(self, suffix):
        if suffix.startswith("/"):
            return f"{self.rwa_prefix}{suffix}"
        return f"{self.rwa_prefix}/{suffix}"

    def _get_api_credentials(self, account_type="primary"):
        """
        For RWA requests, prefer RWA creds; if absent (e.g., generating RWA API),
        fall back to primary. Otherwise default behaviour.
        """
        credentials_map = self._get_api_key_credentials_map()
        if account_type == self.rwa_account_type:
            return credentials_map.get(self.rwa_account_type)
        return credentials_map.get(account_type) or credentials_map.get("primary")

    def get_account_v3_rwa(self, **kwargs):
        """
        Retrieve RWA sub-account data and cache it for later signing.
        """
        path = self._rwa_path("/account")
        accountRes = self._get(
            endpoint=path,
            params=kwargs,
            account_type=self.rwa_account_type,
        )
        data = accountRes.get('data') if isinstance(accountRes, dict) else None
        if data is not None:
            contract_account = data.get('contractAccount') or {}
            sub_accounts = contract_account.get('subAccountInfo') or []
            rwa_sub = next(
                (s for s in sub_accounts if s.get('accountType') == 'SUB_STOCK_ACCOUNT'),
                None,
            )
            if rwa_sub:
                # Promote RWA sub-account id for downstream signing/API calls.
                data = dict(data)
                rwa_account_id = rwa_sub.get('accountId')
                data['stockAccountId'] = rwa_account_id
                data['subAccountId'] = rwa_account_id or data.get('subAccountId')
                data['id'] = rwa_account_id or data.get('id')
                # Flatten contract account for convenience
                data['contractAccount'] = contract_account
                data['spotAccount'] = data.get('spotAccount') or {}
            # Preserve cached l2Key (derived_pubkey) if the API payload omits it.
            cached_rwa_ctx = self._get_account_context(self.rwa_account_type) or {}
            cached_l2_key = (
                data.get('omniSwapAccount', {}).get('l2Key')
                or cached_rwa_ctx.get('l2Key')
            )
            if cached_l2_key and not data.get('l2Key'):
                data['l2Key'] = cached_l2_key
            self._set_account_context(data, account_type=self.rwa_account_type)
        return data

    def _resolve_primary_account(self):
        account = self._get_account_context("primary")
        if not account:
            account = self.get_account_v3()
        if not account:
            raise ValueError('Primary account context is required')
        return account

    def _derive_rwa_seed(self, master_seed_hex):
        """
        Derive a deterministic RWA seed from the primary seed (mirrors web generateStockSeed).
        """
        if not master_seed_hex:
            raise ValueError('Primary seed is required to derive RWA seed')
        clean_master = master_seed_hex.removeprefix('0x')
        try:
            master_seed_bytes = bytes.fromhex(clean_master)
        except ValueError as exc:
            raise ValueError('Primary seed must be hex') from exc

        # Enable HD wallet derivation (eth-account marks as unaudited).
        Account.enable_unaudited_hdwallet_features()

        # 1) hash seed -> 32 bytes entropy
        entropy = hashlib.sha256(master_seed_bytes).digest()
        # 2) entropy -> mnemonic -> derive m/0'/0 on secp256k1
        mnemonic = Mnemonic('english').to_mnemonic(entropy)
        account_path = "m/0'/0"
        acct = Account.from_mnemonic(mnemonic, account_path=account_path)
        priv_hex = acct.key.hex()
        priv_padded = priv_hex.zfill(64)

        # 4) format as eth-style signature string: 0x + r + s + v
        r = priv_padded.ljust(64, '0')
        s = priv_padded.ljust(64, '0')
        v = '1b'
        return f"0x{r}{s}{v}"

    def _build_rwa_registration_signature(self, master_account, master_l2_key):
        """
        RWA registration follows web logic:
        - message uses the *master* l2Key
        - signature and RWA l2Key are produced by the RWA seed signer
        - the RWA l2Key (signer pubkey) is what gets submitted in the request
        """
        if not master_l2_key:
            raise ValueError('Master l2Key is required to build RWA signature')
        l2_key_str = master_l2_key if isinstance(master_l2_key, str) else str(master_l2_key)
        sign_msg = f"Register stock account, main account l2key {l2_key_str}"
        seeds = self.zk_seeds
        if not seeds:
            raise ValueError('zk seeds required to sign RWA registration')
        rwa_seed_hex = self._derive_rwa_seed(seeds)
        rwa_seed_bytes = bytes.fromhex(rwa_seed_hex.removeprefix('0x'))
        rwa_signer = sdk.ZkLinkSigner.new_from_seed(rwa_seed_bytes)
        # Mirror web signing: hash message, reduce by EC order, then sign
        # the reduced value to stay within the signer bit-length limit.
        message_hash_hex = hashlib.sha256(sign_msg.encode()).hexdigest()
        ec_order = int('3618502788666131213697322783095070105526743751716087489154079457884512865583')
        data_bn = int(message_hash_hex, 16)
        data_mod_hex = hex(data_bn % ec_order).removeprefix('0x')
        signature = rwa_signer.sign_musig(data_mod_hex.encode()).signature
        rwa_pubkey = rwa_signer.public_key()
        return signature, rwa_pubkey

    def _build_rwa_api_signature_with_nonce(self, l2_key, eth_address, chain_id=None):
        """
        Generate signature for RWA generate-api using nonce flow (web aligned).
        """
        if not eth_address:
            raise ValueError('eth_address is required for api signature')
        chain_id = chain_id or getattr(self, "network_id", None)
        if chain_id is None:
            raise ValueError('chain_id is required for api signature')

        rwa_seed_hex = self._derive_rwa_seed(self.zk_seeds)
        self.rwa_zk_seeds = rwa_seed_hex
        rwa_seed_bytes = bytes.fromhex(rwa_seed_hex.removeprefix('0x'))
        signer = sdk.ZkLinkSigner.new_from_seed(rwa_seed_bytes)
        pub_key = signer.public_key()

        # Retrieve nonce using derived RWA pubkey
        nonce_res = self.generate_nonce_v3(
            l2Key=str(pub_key).removeprefix('0x').lower(),
            ethAddress=eth_address,
            chainId=chain_id,
        )
        nonce = None
        if isinstance(nonce_res, dict):
            nonce = nonce_res.get('data', {}).get('nonce') or nonce_res.get('nonce')
        if nonce is None:
            raise ValueError('nonce is required for RWA api signature')

        message = f"{str(pub_key).removeprefix('0x')}{eth_address}{nonce}".lower()
        msg_hash = hashlib.sha256(message.encode()).hexdigest()
        ec_order = int('3618502788666131213697322783095070105526743751716087489154079457884512865583')
        data_bn = int(msg_hash, 16)
        data_mod_hex = hex(data_bn % ec_order).removeprefix('0x')
        signature = signer.sign_musig(data_mod_hex.encode()).signature
        return signature, pub_key

    def register_rwa_account_v3(
            self,
            l2Key=None,
    ):
        """
        Register a RWA sub-account for the current user.
        The master account and signature are derived automatically.
        """
        master_l2_key = l2Key or self.zk_l2Key
        if master_l2_key is None:
            raise ValueError('master zk l2Key is required')

        master_account = self._resolve_primary_account()
        master_account_id = master_account.get('id')
        if not master_account_id:
            raise ValueError('Primary account id required for RWA registration')

        signature, rwa_pubkey = self._build_rwa_registration_signature(master_account, master_l2_key)
        l2_key_payload = rwa_pubkey if isinstance(rwa_pubkey, str) else str(rwa_pubkey)

        path = self._rwa_path("/register-account")
        register_res = self._post(
            endpoint=path,
            data={
                'l2Key': l2_key_payload,
                'masterAccountId': master_account_id,
                'signature': signature,
            },
            account_type="primary",
        )

        data = register_res.get('data') if isinstance(register_res, dict) else None
        if data:
            rwa_account = data.get('stockAccount') or {}
            if rwa_account:
                # Promote RWA account context
                account_ctx = {
                    'id': rwa_account.get('accountId'),
                    'stockAccountId': rwa_account.get('accountId'),
                    'accountType': rwa_account.get('accountType'),
                }
                self._set_account_context(account_ctx, account_type=self.rwa_account_type)
        return register_res

    def generate_rwa_api_v3(self, wallet_name, account_id=None, eth_address=None, chain_id=None, l2Key=None, signature=None):
        """
        Generate a trading API for the RWA account using the RWA-specific endpoint.
        """
        # Prefer caller-provided RWA l2Key; otherwise take the RWA account context.
        rwa_account = self._get_account_context(self.rwa_account_type) or {}
        l2_key = l2Key or rwa_account.get('l2Key') or self.zk_l2Key

        if l2_key is None:
            raise ValueError('RWA zk l2Key is required')
        if wallet_name is None:
            raise ValueError('wallet_name is required')
        if account_id is None:
            account_id = rwa_account.get('id')
        if account_id is None:
            raise ValueError('RWA account_id is required')
        if eth_address is None:
            raise ValueError('eth_address is required')
        derived_pubkey = None
        if signature is None:
            chain_id = chain_id or getattr(self, "network_id", None)
            if chain_id is None:
                raise ValueError('chain_id is required to build RWA api signature')
            # Build signature using RWA seed + nonce flow.
            signature, derived_pubkey = self._build_rwa_api_signature_with_nonce(l2_key, eth_address, chain_id)

        l2_key_payload = derived_pubkey or l2_key
        path = self._rwa_path("/generate-api")
        response = self._post(
            endpoint=path,
            data={
                'l2Key': l2_key_payload,
                'walletName': wallet_name,
                'accountId': account_id,
                'ethAddress': eth_address,
                'signature': signature,
            },
            account_type="primary",
        )
        # Cache derived RWA seed even when caller supplies signature/l2Key
        # so downstream RWA signing uses the correct key.
        if not getattr(self, "rwa_zk_seeds", None) and self.zk_seeds:
            try:
                self.rwa_zk_seeds = self._derive_rwa_seed(self.zk_seeds)
            except Exception:
                # Do not block if derivation fails; caller may have provided RWA seeds separately.
                pass
        data = response.get('data') if isinstance(response, dict) else None
        if data:
            rwa_account = data.get('stockAccount') or {}
            api_key_block = rwa_account.get('apiKey') or data.get('apiKey')
            if rwa_account:
                account_ctx = {
                    'id': rwa_account.get('accountId'),
                    'stockAccountId': rwa_account.get('accountId'),
                    'accountType': rwa_account.get('accountType'),
                    'l2Key': derived_pubkey or rwa_account.get('l2Key') or l2_key_payload,
                }
                self._set_account_context(account_ctx, account_type=self.rwa_account_type)
            if api_key_block:
                credentials = {
                    'key': api_key_block.get('key'),
                    'secret': api_key_block.get('secret'),
                    'passphrase': api_key_block.get('passphrase'),
                }
                self.set_rwa_api_credentials(credentials)
        return response

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

    def delete_orders_v3(self, **kwargs):

        path = URL_SUFFIX + "/v3/delete-orders"
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
    def delete_order_by_client_order_ids_v3(self, **kwargs):
        path = URL_SUFFIX + "/v3/delete-client-order-ids"
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

        path = URL_SUFFIX + "/v3/order-by-client-order-id"
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

        path = URL_SUFFIX + "/v3/order-by-client-order-id"
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

    def get_repayment_price_v3(self, repaymentPriceTokens, clientId=None ):

        repaymentPriceTokens = urllib.parse.quote(repaymentPriceTokens)

        clientId = clientId or random_client_id()
        path = URL_SUFFIX + "/v3/repayment-price"
        return self._get(
            endpoint=path,
            params={
                'repaymentPriceTokens':repaymentPriceTokens,
                'clientId': clientId
            }
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

    def withdraws_by_time_and_status_v3(self, **kwargs):
        path = URL_SUFFIX + "/v3/withdraws-by-time-and-status"
        return self._get(
            endpoint=path,
            params=kwargs
        )

    def get_credit_account_v3(self, **kwargs):
        """"
        GET Retrieve credit sub-account information.
        :param kwargs: accountId (required), rsaPublicKeyN, rsaPublicKeyE, signatureForRsaPublicKey (optional)
        :returns: Request results as dictionary.
        """
        path = URL_SUFFIX + "/v3/credit-account"
        res = self._get(
            endpoint=path,
            params=kwargs
        )
        return res.get('data') if isinstance(res, dict) else res

    def get_credit_account_position_risk_v3(self, **kwargs):
        """"
        GET Retrieve credit sub-account position and risk information.
        :returns: Request results as dictionary.
        """
        path = URL_SUFFIX + "/v3/credit-account-position-risk"
        res = self._get(
            endpoint=path,
            params=kwargs
        )
        return res.get('data') if isinstance(res, dict) else res

