from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from PIL import Image
import io
import os
from Crypto.Hash import SHA256, HMAC, SHA1
def decrypt_image(input_image_path, output_image_path, key, iv_path):
  # Read the IV from the separate file
  with open(iv_path, 'rb') as f:
    unique_iv = f.read()
  # Read the encrypted data
  with open(input_image_path, 'rb') as f:
    encrypted_data = f.read()
  # Separate the IV from the encrypted data
  iv = encrypted_data[:AES.block_size]
  encrypted_data = encrypted_data[AES.block_size:]
  # Initialize AES cipher
  cipher = AES.new(key, AES.MODE_CBC, unique_iv)
  # Decrypt the image data
  decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
  # Convert decrypted bytes to image
  decrypted_image = Image.open(io.BytesIO(decrypted_data))
  # Save the decrypted image
  decrypted_image.save(output_image_path, format=decrypted_image.format)
  print(f"Decryption successful. Decrypted image saved to '{output_image_path}'.")
# Example usage
if __name__ == "__main__":
  input_image_path = "encrypted_image.jpg"
  iv_file = '1.jpg.iv'
  key = 'UZ4i59vPgLRT16s8FZ4i81vPgLRT16qk'
  key = bytes(key, encoding="utf-8")
  decrypt_image(input_image_path, 'decrypted_image.jpg', key, iv_file)