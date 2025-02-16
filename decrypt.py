import AES

filename = input("Enter encrypted file name: ")
password = input("Enter password: ")

with open(filename, "r") as file:
    salt_hex = file.readline().strip() # Read salt from the first line'
    salt = bytes.fromhex(salt_hex) # Convert hex to bytes
    encrypted_content = file.read() # Read the encrypted data

key, _ = AES.generate_key(password, salt) # Generate the AES key from password and salt
decrypted_content = AES.decrypt_message(encrypted_content, key)

output_file = filename.replace("log_", "decrypted_") # new file with decrypted content
with open(output_file, "w") as file:
    file.write(decrypted_content)

print(f"Decrypted content saved to {output_file}")
