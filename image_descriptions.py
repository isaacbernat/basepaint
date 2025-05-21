import os
import csv
from time import sleep
from PIL import Image

import google.generativeai as genai

from config import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_SLEEP
from fetch_metadata import load_titles


def create_description_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    titles = load_titles(os.path.join(script_dir, "metadata.csv"))
    metadata_days = {int(k): v["title"] for k, v in titles.items()}
    describe_png_images_to_csv(metadata_days, script_dir)


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


def describe_png_images_to_csv(metadata_days, script_dir):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    reduced_dir = os.path.join(script_dir, "reduced_images")
    description_csv = os.path.join(script_dir, "description.csv")

    existing_ids = set()
    if os.path.exists(description_csv):
        with open(description_csv, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                existing_ids = {int(row["filename"]) for row in reader}
            except Exception as e:
                print(f"Error reading description csv: {e}")

    with open(description_csv, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        if not existing_ids:
            csv_writer.writerow(["filename", "analysis"])

        for filename in sorted(os.listdir(reduced_dir)):
            if filename.endswith(".png"):
                image_id = int(os.path.splitext(filename)[0])
                if image_id in existing_ids:
                    continue
                title_text = metadata_days.get(image_id, "")
                description = analyze_image_with_metadata(model, os.path.join(reduced_dir, filename), title_text)
                if description:
                    for d in description.split("\n"):
                        csv_writer.writerow([image_id, d.strip("*   ")])
                if image_id % GEMINI_SLEEP[0] == 0:
                    print(f"Analyzed image with metadata: {filename} . Sleeping {GEMINI_SLEEP[1]} secs to avoid rate limits.")
                    sleep(GEMINI_SLEEP[1])
    print("Finished creating description csv.")


def create_description_page(canvas, script_dir, page_width, page_height, scaled_width, x_pos, titles, day_num, descriptions):
    title_data = titles.get(int(day_num), {'title': ''})
    title = f"Day {day_num}: {title_data['title']}"
    canvas.setFont("MekSans-Regular", 24)
    canvas.drawString(x_pos, page_height - 55, title)
    canvas.setFont("OpenSans-Italic", 12)  # Italic for descriptive part
    canvas.drawString(x_pos, page_height - 55, f"Description by {GEMINI_MODEL}")

    # TODO implement description    
    # description_lines = descriptions.get(int(day_num), "")
    # for line_num, l in enumerate(description_lines.split("\n")):
    #     canvas.drawString(x_pos, page_height - 55 - line_num * 12, l)
