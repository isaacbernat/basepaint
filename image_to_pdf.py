from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import csv

def load_titles(csv_path):
    titles = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles[int(row['NUM'])] = row['TITLE']
    return titles

def create_pdf_from_images(input_directory, output_pdf, titles):
    # Set up the PDF canvas with A4 size
    c = canvas.Canvas(output_pdf, pagesize=A4)

    # A4 dimensions in points (1 point = 1/72 inch)
    page_width, page_height = A4
    
    # Define image size (2560x2560 pixels converted to points)
    img_size = 2560 * 72 / 96  # Convert pixels to points (96 DPI to 72 DPI)
    
    # Calculate scaling factor to fit width while maintaining aspect ratio
    scale_factor = (page_width * 0.9) / img_size  # 90% of page width
    
    # Calculate scaled dimensions
    scaled_width = img_size * scale_factor
    scaled_height = img_size * scale_factor
    
    # Calculate x position to center image
    x_pos = (page_width - scaled_width) / 2
    
    # Get list of JPEG images
    image_files = [f for f in os.listdir(input_directory) 
                  if f.lower().endswith('.jpg')]
    image_files.sort()  # Sort files alphabetically
    
    # Process each image
    for page_num, image_file in enumerate(image_files, 1):
        # Extract day number from filename (assuming XXXX.jpg format)
        day_num = int(image_file.split('.')[0])
        if page_num % 10 == 0:
            print(f"Processing image {day_num}")
        image_path = os.path.join(input_directory, image_file)
        
        # Add title with day number and title from CSV
        title = f"Day {day_num}: {titles.get(day_num, '')}"
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_pos, page_height - 50, title)
        
        # Add image
        c.drawImage(image_path, 
                   x_pos,  # center horizontally
                   page_height - scaled_height - 70,  # position below title
                   width=scaled_width, 
                   height=scaled_height)
        
        c.showPage()
    
    c.save()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "images")
    csv_path = os.path.join(script_dir, "gallery_titles.csv")

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        exit(1)

    # Load titles from CSV
    titles = load_titles(csv_path)

    # Extract the highest day number from filenames
    image_files = [f for f in os.listdir(img_dir) if f.lower().endswith('.jpg')]
    if not image_files:
        print("No images found in the images directory")
        exit(1)
    
    # Extract the highest day number from filenames
    last_day = max(int(f.split('.')[0]) for f in image_files)
    output_pdf = os.path.join(script_dir, f"basepaint_until_{last_day:04d}.pdf")

    create_pdf_from_images(img_dir, output_pdf, titles)
    print(f"PDF has been created: {output_pdf}")
