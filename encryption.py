import random, math

def is_prime(n, k=5):  # Miller-Rabin primality test
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randint(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=512): # Generate a large prime number
    while True:
        num = random.getrandbits(bits)
        if is_prime(num):
            return num

def gcd(a, b):# find the greatest common divisor
    while b:
        old_a = a
        a = b
        b = old_a % b
    return a

# Compute modular inverse (Extended Euclidean Algorithm)
def mod_inverse(e, phi):
    old_r, r = e, phi
    old_s, s = 1, 0

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    if old_s < 0:
        old_s += phi
    return old_s

# Generate RSA keys
def generate_keys(bits=512):
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose public exponent e
    e = 65537  # Common value for e
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)

    # Compute private exponent d
    d = mod_inverse(e, phi)
    
    return ((e, n), (d, n))  # Public and private keys

# Encrypt a message
def encrypt(plaintext, public_key):
    e, n = public_key
    cipher = [pow(ord(char), e, n) for char in plaintext]
    return cipher

# Decrypt a message
def decrypt(ciphertext, private_key):
    d, n = private_key
    plaintext = ''.join(chr(pow(char, d, n)) for char in ciphertext)
    return plaintext

# # Example usage
# public_key, private_key = generate_keys(bits=512)

# message = "Hello, RSA!"
# print("Original Message:", message)

# # Encrypt the message
# encrypted_msg = encrypt(message, public_key)
# print("Encrypted:", encrypted_msg)

# # Decrypt the message
# decrypted_msg = decrypt(encrypted_msg, private_key)
# print("Decrypted:", decrypted_msg)
