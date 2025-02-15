import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# Generate a secure encryption key from a password
def generate_key(password, salt=None):
    if salt is None:
        salt = get_random_bytes(16)  # 16-byte random salt
    key = PBKDF2(password, salt, dkLen=32)  # AES-256 key
    return key, salt

# Padding function for AES block size (16 bytes)
def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + (chr(padding_length) * padding_length).encode()

# Unpadding function
def unpad(data):
    return data[:-ord(data[-1:])]

# Encrypt a message
def encrypt_message(message, key):
    message = pad(message.encode())  # Convert to bytes and pad
    iv = get_random_bytes(16)  # Generate a random IV (Initialization Vector)
    cipher = AES.new(key, AES.MODE_CBC, iv)  # AES-256 in CBC mode
    encrypted = cipher.encrypt(message)
    return base64.b64encode(iv + encrypted).decode()  # Encode in base64

# Decrypt a message
def decrypt_message(encrypted_message, key):
    data = base64.b64decode(encrypted_message)  # Decode base64
    iv, encrypted = data[:16], data[16:]  # Extract IV and encrypted message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted))
    return decrypted.decode()
