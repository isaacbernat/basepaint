import os
import csv
from PIL import Image

import google.generativeai as genai

from config import GOOGLE_API_KEY, GEMINI_MODEL


def create_description_pdf(batch_size=100):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    describe_png_images_to_csv(script_dir)


def create_reduced_images(block_size=2, output_format="png"):
    """
    Original images have square blocks many pixels tall. Shrink them using the top-left pixel.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(script_dir, "images")
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
    reduced_dir = os.path.join(script_dir, "reduced_images")
    os.makedirs(reduced_dir, exist_ok=True)  # Create pdf directory if needed

    for image_file in image_files:  # Process each image
        image_name = image_file.split(".")[0]
        output_img = os.path.join(reduced_dir, f"{image_name}.{output_format}")
        if int(image_name) % 10 == 0:
            print(f"Reducing image: {image_file}. Will skip those already present.")
        if os.path.exists(output_img):
            continue

        try:
            img = Image.open(os.path.join(image_dir, image_file))
            width, height = img.size
            new_width = width // block_size
            new_height = height // block_size  # square images could use width instead
            reduced_image = Image.new("RGB", (new_width, new_height))
            reduced_pixels = reduced_image.load()
            original_pixels = img.load()

            # Take the color of the top-left pixels of the original blocks
            for y_new in range(new_height):
                for x_new in range(new_width):
                    x_original = x_new * block_size
                    y_original = y_new * block_size
                    color = original_pixels[x_original, y_original]
                    reduced_pixels[x_new, y_new] = color
            reduced_image.save(output_img)

        except Exception as e:
            print(f"An error occurred processing {image_name}: {e}")


def analyze_image_with_metadata(model, image_path, title_text):
    res = ""
    # TODO move (and improve) description to config.py.
    prompt_text = f"Analize in detail this pixel art image from basepaint.xyz project.{title_text} Identify all notable elements with emphasis to Internet meme references, including cultural, popular, tv, games and other too. Highlight each reference in bullet points. No need to start the answer with an introduction, just sort the ouput bullet points according to the image positions, starting from top and left corner. You may include a list with the lest prominent elements at the end of the message, under their own bullet point."
    try:
        img = Image.open(image_path)
        response = model.generate_content([prompt_text, img])
        res = response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error during analysis of image {image_path}: {e}")
    finally:
        return res


def describe_png_images_to_csv(script_dir):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    reduced_dir = os.path.join(script_dir, "reduced_images")
    description_csv = os.path.join(script_dir, "description.csv")
    metadata_csv = os.path.join(script_dir, "metadata.csv")

    existing_days = dict()
    if os.path.exists(metadata_csv):  # Read existing days from CSV if it exists
        with open(metadata_csv, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_days = {int(row['NUM']): {row['TITLE']} for row in reader}

    mode = 'a' if existing_days else 'w'  # Open in append mode if file exists, write mode if it doesn't
    with open(description_csv, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['filename', 'analysis'])

        for filename in os.listdir(reduced_dir):
            if filename.endswith(".png"):
                image_id = int(os.path.splitext(filename)[0])
                title_text = existing_days.get(image_id, "")
                if image_id % 10 == 0:
                    print(f"Analyze image with metadata: {filename}")
                csv_writer.writerow([image_id, analyze_image_with_metadata(model, os.path.join(reduced_dir, filename), title_text)])
    print("Finished creating description csv.")
