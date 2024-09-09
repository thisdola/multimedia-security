from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_private_key,load_der_public_key
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
#import tensorflow as tf
import numpy as np






class DH():
    def __init__(self):
        self.__g = 2
        self.__p = 23655560277314464226619676212758329093123755902275162377165556656407018949884478108852157120238956692560730593356156677495348607394439529671315837124469826767869644005310080643758064019453756537882464958611408605258384300683826619416189074611201222084715456568354827638243684257506448013767375341250292564417913967651873066563558555800690368198391317087360423260297222640722501595322331096309026375135048608200153935070606824703302598731896612085322264832083111396074165216144374191309825231700945420037752046736008372198136083286921241558806302262229447112826555248626158815640360741308740070054947013420147586163303
        self.params_numbers = dh.DHParameterNumbers(self.__p,self.__g)
        self.params = self.params_numbers.parameters(backend=default_backend())

    def generate_dh_key_pair(self):
        self.private_key = self.params.generate_private_key()
        self.public_key = self.private_key.public_key()
        return self.public_key.public_bytes(Encoding.DER,PublicFormat.SubjectPublicKeyInfo)
    
    
    def parse_key(self,key):
        return load_der_public_key(key,backend=default_backend())
    
    def compute_shared_secret(self, peer_public_key:bytes):
        shared_secret = self.private_key.exchange(self.parse_key(peer_public_key))
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_secret)
        return derived_key

"""
    def generate_key_from_dh(shared_secret:bytes, image_shape):
        key = np.frombuffer(shared_secret, dtype=np.uint8)
        key = np.resize(key, image_shape)
        return tf.constant(key, dtype=tf.uint8)
    
    """







