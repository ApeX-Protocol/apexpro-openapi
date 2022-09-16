import os
import sys

from apexpro.helpers.request_helpers import calc_bind_owner_key_sig_hash, starkex_sign, starkex_verify, key_sig_hash, \
    starkex_sign2

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)


print("Hello, Apexpro")

hash = calc_bind_owner_key_sig_hash('06fe2d2c7f5cc13ac1a1efc2abb68e51ab8e21ab873b95e819979c8013e0ddcb', "0x8ef200ee0cba6e05c212048a2c571e80b76ff8ed")
print(hash.hex())

signature = starkex_sign(hash, '0x30ed61554cc70daf58e0eaa8feb65a9b0d020aee4852069ff80b093eed57019')
print("signature:" + signature)

bVerify = starkex_verify(hash, signature, '0x5dc8baaed55578aeec543274677e71dcf649d11e926fe0c5f108460fcd960a5')
print("Verify:" +str( bVerify))



