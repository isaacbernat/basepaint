from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
from datetime import datetime

def create_pdf_from_images(input_directory, output_pdf):
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
                  if f.lower().endswith(('.jpg', '.jpeg'))]
    image_files.sort()  # Sort files alphabetically
    
    # Fixed datetime for all pages
    current_time = datetime.fromisoformat("2024-12-12T21:47:06+01:00")
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Process each image
    for page_num, image_file in enumerate(image_files, 1):
        image_path = os.path.join(input_directory, image_file)
        
        # Add title with datetime and page number
        title = f"{formatted_time} - Page {page_num}"
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
    
    output_pdf = os.path.join(script_dir, "output.pdf")
    img_dir = os.path.join(script_dir, "images")

    create_pdf_from_images(img_dir, output_pdf)
    print(f"PDF has been created: {output_pdf}")
