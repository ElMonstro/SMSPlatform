from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from base64 import b64decode

# 1024 means the keysize will be 1024 bits
def generate_encryption_keys():
    key_pair = RSA.generate(1024)
    with open("privatekey.pem", "w") as private_key:
        private_key.write(key_pair.exportKey().decode("utf-8"))
    with open("public_key.pem", "w") as public_key:
        public_key.write(key_pair.publickey().exportKey().decode("utf-8"))



def decrypt_string(encrypted_string):
    key_string = None
    with open("public_key.pem", "r") as file:
        key_string = file.read()

    key = RSA.importKey(key_string)
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
    return cipher.decrypt(b64decode(encrypted_string))
