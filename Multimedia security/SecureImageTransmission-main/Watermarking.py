#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from PIL import Image

class Watermarking:
    def __init__(self, image_path, output_path, watermark_text):
        self.image_path = image_path
        self.output_path = output_path
        self.watermark_text = watermark_text
        self.image = None
        self.pixels = None

    def load_image(self):
        self.image = Image.open(self.image_path)
        self.pixels = self.image.load()

    @staticmethod
    def str_to_bin(s):
        return ''.join(format(c, '08b') for c in s)

    def embed_watermark(self):
        self.load_image()
        binary_watermark = self.str_to_bin(self.watermark_text)
        width, height = self.image.size

        if width * height < len(binary_watermark):
            raise ValueError("Image is too small to hold the watermark")

        index = 0
        for y in range(height):
            for x in range(width):
                if index < len(binary_watermark):
                    pixel = self.pixels[x, y]
                    if len(pixel) == 3:
                        r, g, b = pixel
                        new_r = (r & ~1) | int(binary_watermark[index])
                        self.pixels[x, y] = (new_r, g, b)
                    else:  # RGBA case
                        r, g, b, a = pixel
                        new_r = (r & ~1) | int(binary_watermark[index])
                        self.pixels[x, y] = (new_r, g, b, a)
                    index += 1
                else:
                    break
            if index >= len(binary_watermark):
                break

        self.image.save(self.output_path)
        print("Watermark embedded successfully.")

