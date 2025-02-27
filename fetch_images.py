import requests
import os


def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download image from {url}")


def fetch_images(latest):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, "images")
    os.makedirs(images_dir, exist_ok=True)  # Create images directory if needed

    skipped_days = []
    print("Fetching images...")
    for day in range(1, latest):
        path = os.path.join(images_dir, f"{day:04d}.jpg")
        if os.path.exists(path):
            skipped_days.append(day)  
            continue

        image_url = f"https://basepaint.xyz/api/art/image?day={day}"  # jpg image 2560x2560
        # available in png at lower res too at https://basepaint.net/v3/{day:04d}.png
        download_image(image_url, path)
        if day % 10 == 0:
            print(f"Downloading image {day}")
    print(f"Skipped days (already downloaded): {skipped_days}")
    print("Finished downloading images.")
