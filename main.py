import cv2
import numpy as np
import string
from cryptography.fernet import Fernet
import random

# Generate a secure key for encryption (Save this key securely)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load the encryption key
def load_key():
    return open("secret.key", "rb").read()

# Encrypt the message
def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    encrypted_message = cipher_suite.encrypt(message.encode())
    print("Encrypted Message:", encrypted_message.decode())
    return encrypted_message

# Decrypt the message
def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key)
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
    return decrypted_message

# Convert text to binary
def text_to_binary(data):
    return ''.join(format(byte, '08b') for byte in data)

# Convert binary to text
def binary_to_text(binary_data):
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return bytes([int(b, 2) for b in byte_data])

# Generate a random password using string module
def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Encode the data into the image
def hide_data(image_path, secret_message):
    image = cv2.imread(image_path) # Load the image
    if image is None:
        raise ValueError("Image not found!")

    key = load_key()
    encrypted_message = encrypt_message(secret_message, key)
    binary_message = text_to_binary(encrypted_message + b'####')  # '####' as a delimiter
    
    data_index = 0
    data_length = len(binary_message)
    height, width, channels = image.shape

    if data_length > height * width * 3:
        raise ValueError("Data is too large to hide in this image!")

    # Hide data in pixels
    for row in range(height):
        for col in range(width):
            pixel = image[row, col]
            for channel in range(3):
                if data_index < data_length:
                    pixel[channel] = np.uint8(pixel[channel] & ~1 | int(binary_message[data_index]))
                    data_index += 1
                else:
                    break
    cv2.imwrite("encoded_image.png", image)
    print("Data successfully hidden in 'encoded_image.png'.")

# Extract the data from the image
def extract_data(encoded_image_path):
    image = cv2.imread(encoded_image_path)
    if image is None:
        raise ValueError("Image not found!")

    binary_data = ""
    height, width, channels = image.shape

    for row in range(height):
        for col in range(width):
            pixel = image[row, col]
            for channel in range(3):
                binary_data += str(pixel[channel] & 1)
    print("Extracted Binary Data (first 100 bits):", binary_data[:100])

    extracted_bytes = binary_to_text(binary_data)
    extracted_message = extracted_bytes.split(b'####')[0]  # Extract the actual message
    
    key = load_key()
    decrypted_message = decrypt_message(extracted_message, key)

    # Ensure the message contains only printable characters
    printable_chars = set(string.printable)
    cleaned_message = ''.join(filter(lambda x: x in printable_chars, decrypted_message))
    
    return cleaned_message

# Example 
if __name__ == "__main__":
    generate_key()  
    
    secret_message = "Confidential Data: Project XYZ"
    image_path = "image.jpg"  # input image
    
    # Hide the data
    hide_data("image.jpg", secret_message)

    # Extract the data
    extracted_text = extract_data("encoded_image.png")
    print("Extracted Message:", extracted_text)
