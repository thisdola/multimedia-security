#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from PIL import Image

class DetectAndRemove:
    def __init__(self, image_path, watermark_text, output_path):
        self.image_path = image_path
        self.watermark_text = watermark_text
        self.output_path = output_path
        self.image = None
        self.pixels = None

    def load_image(self):
        self.image = Image.open(self.image_path)
        self.pixels = self.image.load()

    @staticmethod
    def str_to_bin(s):
        return ''.join(format(c, '08b') for c in s)

    @staticmethod
    def bin_to_str(b):
        chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
        return ''.join(chars)

    def check_watermark(self):
        self.load_image()
        binary_watermark = self.str_to_bin(self.watermark_text)
        extracted_watermark = ''
        width, height = self.image.size

        for y in range(height):
            for x in range(width):
                if len(extracted_watermark) < len(binary_watermark):
                    pixel = self.pixels[x, y]
                    if len(pixel) == 3:
                        r, g, b = pixel
                    else:  # RGBA case
                        r, g, b, a = pixel
                    extracted_watermark += str(r & 1)
                else:
                    break
            if len(extracted_watermark) >= len(binary_watermark):
                break

        extracted_text = self.bin_to_str(extracted_watermark)
        print(f"Extracted watermark: {extracted_text}")
        return extracted_watermark == binary_watermark

    def remove_watermark(self):
        self.load_image()
        width, height = self.image.size

        for y in range(height):
            for x in range(width):
                pixel = self.pixels[x, y]
                if len(pixel) == 3:
                    r, g, b = pixel
                    new_r = r & ~1
                    self.pixels[x, y] = (new_r, g, b)
                else:  # RGBA case
                    r, g, b, a = pixel
                    new_r = r & ~1
                    self.pixels[x, y] = (new_r, g, b, a)

        self.image.save(self.output_path)
        print("Watermark removed successfully.")

