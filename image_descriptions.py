import os
from PIL import Image
import google.generativeai as genai
import csv
from config import GOOGLE_API_KEY, GEMINI_MODEL


def create_description_pdf(batch_size=100):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    describe_png_images_to_csv(script_dir)


def create_reduced_images(script_dir, block_size, output_format="png"):
    """
    Original images have square blocks many pixels tall to be shrinked using the top-left pixel.
    """
    image_dir = os.path.join(script_dir, "images")
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])

    reduced_dir = os.path.join(script_dir, "reduced_images")
    os.makedirs(reduced_dir, exist_ok=True)  # Create pdf directory if needed

    for image_file in image_files:  # Process each image
        image_name = image_file.split(".")[0]
        output_img = os.path.join(reduced_dir, f"image_name.{output_format}")
        if os.path.exists(output_img):
            print(f"Skipping {output_img} as it already exists")

        image_path = os.path.join(image_dir, image_file)

        try:
            img = Image.open(image_path)
            width, height = img.size
            new_width = width // block_size
            new_height = height // block_size
            reduced_image = Image.new("RGB", (new_width, new_height))
            reduced_pixels = reduced_image.load()
            original_pixels = img.load()

            for y_new in range(new_height):
                for x_new in range(new_width):
                    # Coordinates of the top-left pixel of the original block
                    x_original = x_new * block_size
                    y_original = y_new * block_size

                    # Take the color of the top-left pixel of the original block
                    color = original_pixels[x_original, y_original]
                    reduced_pixels[x_new, y_new] = color

            # Construct the output file path
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{image_name}.{output_format}"
            output_path = os.path.join(reduced_dir, output_filename)

            # Save the reduced image
            reduced_image.save(output_path)
            return output_path

        except Exception as e:
            print(f"An error occurred: {e}")
            return None


def describe_png_images_to_csv(script_dir):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    reduced_dir = os.path.join(script_dir, "reduced_images")
    description_csv = os.path.join(script_dir, "description.csv")

    with open(description_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['filename', 'analysis'])

        for filename in os.listdir(reduced_dir):
            if filename.endswith(".png"):
                image_path = os.path.join(reduced_dir, filename)
                # img = open(image_path, 'rb').read()
                img = Image.open(image_path)
                response = model.generate_content([
                    # TODO move (and improve) description to config.py
                    "Analiza detalladamente esta imagen de pixel art e identifica todos los elementos destacables que puedan ser referencias a memes conocidos, personajes de videojuegos, o elementos culturales populares. Describe brevemente cada elemento.",
                    img
                ])
                csv_writer.writerow([description_csv, response.candidates[0].content.parts[0].text])
