import os
import random
import math
import colorsys
import shutil
from PIL import Image

# VARIABLES
spread_amount_scale = 1.6
saturation_addition = 0.15
hue_shift_apply = 0.3
noise_percentage = 0.2
noise_strength = 30
color_reduction = 16

# FUNCTIONS

def clamp(value: float, min_value: float, max_value: float) -> float:
  return max(min_value, min(value, max_value))

def lerp(start: float, end: float, alpha: float) -> float:
  return start + alpha * (end - start)

# Offset/spread pixels randomly in a texture
def spread_pixels(image: Image):
  new_image = image.copy()
  width, height = image.size
  amount = int(math.sqrt(width * height) * spread_amount_scale)
  for i in range(amount):
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    pixel = image.getpixel((x, y))

    for j in range(5):
      x_plot = x + random.randint(-2, 2)
      y_plot = y + random.randint(-2, 2)
      if x_plot < 0 or x_plot >= width: continue
      if y_plot < 0 or y_plot >= height: continue
      if x_plot == x or y_plot == y: continue

      pixel_plot = image.getpixel((x_plot, y_plot))
      new_image.putpixel((x_plot, y_plot), pixel)
      new_image.putpixel((x, y), pixel_plot)
      break

  return new_image

# Shift hue in a texture
def shift_hue(image: Image):
  width, height = image.size
  shift = random.random() * 0.8 + 0.1

  for x in range(width):
    for y in range(height):
      old_pixel = image.getpixel((x, y))
      ro, go, bo = (old_pixel[0] / 255.0, old_pixel[1] / 255.0, old_pixel[2] / 255.0)

      # Convert RGB values (0–255) to HSV (where RGB must be in 0–1 range)
      h, s, v = colorsys.rgb_to_hsv(ro, go, bo)

      s = min(s + saturation_addition, 1.0)

      # Shift hue and wrap around if necessary
      h = (h + shift) % 1.0  # Hue stays within [0, 1] range

      # Convert HSV back to RGB
      rn, gn, bn = colorsys.hsv_to_rgb(h, s, v)
      rn = lerp(ro, rn, hue_shift_apply)
      gn = lerp(go, gn, hue_shift_apply)
      bn = lerp(bo, bn, hue_shift_apply)

      # Convert RGB values back to integer range (0–255)
      if image.mode == "RGBA":
        new_pixel = (int(rn * 255), int(gn * 255), int(bn * 255), old_pixel[3])
      else:
        new_pixel = (int(rn * 255), int(gn * 255), int(bn * 255))

      # Apply new pixel value
      image.putpixel((x, y), new_pixel)
  return

# Make random noise in a texture
def make_noise(image: Image):
  width, height = image.size
  for x in range(width):
    for y in range(height):
      if random.random() > noise_percentage:
        continue
      r, g, b, a = image.getpixel((x, y))
      if a < 20:
        continue
      r, g, b = tuple(clamp(p + random.randint(-noise_strength, noise_strength), 0, 255) for p in (r, g, b))  # Invert RGB
      image.putpixel((x, y), (r, g, b, a))
  return

# Low res colors
def low_color(image: Image):
  width, height = image.size
  for x in range(width):
    for y in range(height):
      old_pixel = image.getpixel((x, y))
      new_pixel = tuple((int(p / color_reduction) * color_reduction) for p in old_pixel[:3])
      if image.mode == "RGBA":
        p = list(new_pixel)
        p.append(old_pixel[3])
        new_pixel = tuple(p)
      else:
        new_pixel = new_pixel
      image.putpixel((x, y), new_pixel)
  return

# START CODE

# Get the script's working directory
working_dir = os.getcwd()

# Define the input and output directories within the working directory
input_dir = os.path.join(working_dir, "input")
output_dir = os.path.join(working_dir, "output")

# Walk through the input directory tree
for root, dirs, files in os.walk(input_dir):
  for file in files:
    # Specify the input file path
    input_path = os.path.join(root, file)

    # Determine the relative path from the input directory
    rel_dir = os.path.relpath(root, input_dir)

    # Create the same subdirectory structure in the output directory
    dest_dir = os.path.join(output_dir, rel_dir)

    # Create an empty directory if not exists
    if not os.path.exists(dest_dir):
      os.makedirs(dest_dir)

    # Specify the output file path
    output_path = os.path.join(dest_dir, file)

    if file.lower().endswith('.png'):
      # Open the image file
      image = Image.open(input_path)

      if image.mode != 'RGBA':
        image = image.convert('RGBA')

      image = spread_pixels(image)
      shift_hue(image)
      make_noise(image)
      low_color(image)

      # Save the inverted image in the output folder, preserving the relative path
      image.save(output_path)
      print(f"Modified image saved: {output_path}")
    else:
      # Copy all the metadata across.
      shutil.copy(input_path, output_path)
      print(f"Copied file across: {output_path}")

print("Done!")
