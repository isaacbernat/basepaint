import requests
import os
LATEST = 12

def download_image(url, filename):
  response = requests.get(url, stream=True)
  if response.status_code == 200:
    with open(filename, 'wb') as f:
      for chunk in response.iter_content(1024):
        f.write(chunk)
  else:
    print(f"Failed to download image from {url}")


# Create images directory if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, "images")
os.makedirs(images_dir, exist_ok=True)

for day in range(1, LATEST):
  path = os.path.join(images_dir, f"{day:04d}.jpg")
  if os.path.exists(path):
    continue

  image_url = f"https://basepaint.xyz/api/art/image?day={day}"  # jpg image 2560x2560
  # available in png at lower res too at https://basepaint.net/v3/{day:04d}.png
  download_image(image_url, path)
  if day % 10 == 0:
    print(f"Downloading image {day}")

print("All images downloaded (if successful).")
