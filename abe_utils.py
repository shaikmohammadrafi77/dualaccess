import os

def encrypt_file(file_path, access_policy):
    """
    Dummy CP-ABE encryption: just copies file with '.enc' suffix.
    """
    encrypted_path = file_path + '.enc'
    with open(file_path, 'rb') as f:
        data = f.read()
    with open(encrypted_path, 'wb') as f:
        f.write(data[::-1])  # simple dummy encryption: reverse bytes
    return encrypted_path

def decrypt_file(encrypted_path, user_attributes):
    """
    Dummy CP-ABE decryption: reverse bytes back
    Checks if user_attributes match dummy policy (always True for demo)
    """
    with open(encrypted_path, 'rb') as f:
        data = f.read()
    decrypted_path = encrypted_path.replace('.enc','')
    with open(decrypted_path, 'wb') as f:
        f.write(data[::-1])
    return decrypted_path
