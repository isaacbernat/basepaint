import requests

def download_image(url, filename):
  response = requests.get(url, stream=True)
  if response.status_code == 200:
    with open(filename, 'wb') as f:
      for chunk in response.iter_content(1024):
        f.write(chunk)
  else:
    print(f"Failed to download image from {url}")

for day in range(2, 475):  # 475
  image_url = f"https://basepaint.xyz/api/art/image?day={day}"
  filename = f"basepaint_day_{day}.jpg"
  download_image(image_url, filename)
  if day % 10 == 0:
    print(f"Downloading image {day}")

print("All images downloaded (if successful).")
