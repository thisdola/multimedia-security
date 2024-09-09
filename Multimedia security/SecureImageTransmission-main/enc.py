from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from PIL import Image
import io
import os
from Crypto.Hash import SHA256, HMAC
def encrypt_image(input_image_path, output_image_path, key):
  # Load the image
  image = Image.open(input_image_path)
  # Generate a random IV
  iv = get_random_bytes(AES.block_size)
  # Get a unique identifier from the filename
  image_hash = SHA256.new(os.path.basename(input_image_path).encode("utf-8")).hexdigest()
  # Combine key-specific value with random string (nonce) using HMAC
  key_specific = HMAC.new(key, msg=image_hash.encode("utf-8"), digestmod=SHA256).digest()
  unique_iv = HMAC.new(key_specific, msg=os.urandom(16), digestmod=SHA256).digest()[:16]
  if len(unique_iv) != 16:
    raise ValueError("Unexpected IV length. Encryption aborted.")
  # Convert the image to bytes
  img_byte_array = io.BytesIO()
  image.save(img_byte_array, format=image.format)
  img_bytes = img_byte_array.getvalue()
  # Initialize AES cipher
  cipher = AES.new(key, AES.MODE_CBC, unique_iv)
  # Encrypt the image data with padding
  padded_data = pad(img_bytes, AES.block_size)
  encrypted_data = iv + cipher.encrypt(padded_data)
  # Write the encrypted data to the output image file
  with open(output_image_path, 'wb') as f:
    f.write(encrypted_data)
  # Save the IV to a separate file with a filename related to the image
  iv_path = os.path.join(os.path.dirname(output_image_path), f"{os.path.basename(input_image_path)}.iv")
  with open(iv_path, 'wb') as f:
      f.write(unique_iv)
  print(f"Encryption successful. Encrypted image saved to '{output_image_path}'.")
  print(f"IV file saved to '{iv_path}'.")
if __name__ == "__main__":
  input_image_path = '1.jpg'
  output_image_path = 'encrypted_image.jpg'
  key = 'UZ4i59vPgLRT16s8FZ4i81vPgLRT16qk'
  key = bytes(key, encoding="utf-8")
  # Encrypt the image
  encrypt_image(input_image_path, output_image_path, key)