import AES

key, salt = AES.generate_key(input("Enter password: "), input("Enter salt: "))
filename = input("File name: ")

with open(filename + 'decrypted', "a") as file:
    file.write(AES.decrypt_message(filename, key))

# message = AES.decrypt_message(filename, key)