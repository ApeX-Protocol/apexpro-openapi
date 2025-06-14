from web3 import Web3

from apexomni.eth_signing import util
from apexomni.eth_signing.sign_off_chain_action import SignOffChainAction

EIP712_ETH_PRIVATE_ACTION_STRUCT_STRING = [
    {'type': 'string', 'name': 'method'},
    {'type': 'string', 'name': 'requestPath'},
    {'type': 'string', 'name': 'body'},
    {'type': 'string', 'name': 'timestamp'},
]
EIP712_ETH_PRIVATE_ACTION_STRUCT_STRING_STRING = (
    'apex(' +
    'string method,' +
    'string requestPath,' +
    'string body,' +
    'string timestamp' +
    ')'
)
EIP712_STRUCT_NAME = 'apex'


class SignEthPrivateAction(SignOffChainAction):

    def get_eip712_struct(self):
        return EIP712_ETH_PRIVATE_ACTION_STRUCT_STRING

    def get_eip712_struct_name(self):
        return EIP712_STRUCT_NAME

    def get_eip712_message(
        self,
        method,
        request_path,
        body,
        timestamp,
    ):
        return super(SignEthPrivateAction, self).get_eip712_message(
            method=method,
            requestPath=request_path,
            body=body,
            timestamp=timestamp,
        )

    def get_hash(
        self,
        method,
        request_path,
        body,
        timestamp,
    ):
        data = [
            [
                'bytes32',
                'bytes32',
                'bytes32',
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(
                    EIP712_ETH_PRIVATE_ACTION_STRUCT_STRING_STRING,
                ),
                util.hash_string(method),
                util.hash_string(request_path),
                util.hash_string(body),
                util.hash_string(timestamp),
            ],
        ]
        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
