from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import csv
from datetime import datetime

def load_titles(csv_path):
    titles = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles[int(row['NUM'])] = {
                'title': row['TITLE'],
                'palette': [tuple(map(int, color.strip().split(','))) for color in row['PALETTE'].split(';')],
                'minted': row.get('MINTED', 0),
                'artists': row.get('ARTISTS', 0),
                'proposer': row.get('PROPOSER', ''),
                'MINT_DATE': row.get('MINT_DATE', '')
            }
    return titles

def count_pixels(image_path, palette):
    image = Image.open(image_path)
    image = image.convert("RGB")  # Ensure image is in RGB mode
    pixel_count = [0] * len(palette)

    color_dict = {tuple(color): index for index, color in enumerate(palette)}

    for pixel in image.getdata():
        if pixel in color_dict:
            pixel_count[color_dict[pixel]] += 1

    total_pixels = image.width * image.height
    percentage_count = [(count / total_pixels) * 100 for count in pixel_count]
    return percentage_count

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
        
        # Get title and palette data
        title_data = titles.get(day_num, {'title': '', 'palette': []})
        
        # Add title with day number and title from CSV
        title = f"Day {day_num}: {title_data['title']}"
        c.setFont("Helvetica-Bold", 14)
        title_width = c.stringWidth(title, "Helvetica-Bold", 14)
        c.drawString(x_pos, page_height - 50, title)
        
        # Draw color squares
        square_size = c.stringWidth("O", "Helvetica-Bold", 14)  # Size of capital O
        square_spacing = square_size * 1.2  # Add some spacing between squares
        palette = title_data['palette']
        total_palette_width = len(palette) * square_spacing
        start_x = page_width - x_pos - total_palette_width
        
        for i, color in enumerate(palette):
            c.setFillColorRGB(color[0]/255, color[1]/255, color[2]/255)
            c.setStrokeColorRGB(0, 0, 0)  # Set border color to black
            c.rect(start_x + (i * square_spacing), 
                  page_height - 50 - square_size/2, 
                  square_size, square_size, 
                  fill=1, stroke=1)  # stroke=1 to draw the border

        # Reset fill color to black for subsequent text
        c.setFillColorRGB(0, 0, 0)
        
        # Add day and date information
        c.setFont("Helvetica", 12)
        day_text = f"Day: {day_num}"
        mint_timestamp = title_data.get('MINT_DATE', '')
        formatted_mint_date = datetime.fromtimestamp(int(mint_timestamp)).strftime('%Y-%m-%d') if mint_timestamp else ''
        date_text = f"Mint date: {formatted_mint_date}"
        
        # Start position for first line (day/date)
        first_line_y = page_height - scaled_height - 90
        
        # Draw day (left-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        c.drawString(x_pos, first_line_y, "Day:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(x_pos + c.stringWidth("Day:", "Helvetica-Oblique", 12), first_line_y, f" {day_num}")
        
        # Draw date (right-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        date_width = c.stringWidth("Mint date:", "Helvetica-Oblique", 12)
        c.drawString(page_width - x_pos - date_width - c.stringWidth(formatted_mint_date, "Helvetica", 12), first_line_y, "Mint date:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(page_width - x_pos - c.stringWidth(formatted_mint_date, "Helvetica", 12), first_line_y, f" {formatted_mint_date}")
        
        # Add theme and proposer information (second line)
        theme_text = f"Theme: {title_data.get('title', '')}"
        proposer_text = f"Proposer: {title_data.get('proposer', '')}"
        
        theme_y = first_line_y - 20  # 20 pixels below first line
        
        # Draw theme (left-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        c.drawString(x_pos, theme_y, "Theme:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(x_pos + c.stringWidth("Theme:", "Helvetica-Oblique", 12), theme_y, f" {title_data.get('title', '')}")
        
        # Draw proposer (right-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        proposer_width = c.stringWidth("Proposer:", "Helvetica-Oblique", 12)
        c.drawString(page_width - x_pos - proposer_width - c.stringWidth(title_data.get('proposer', ''), "Helvetica", 12), theme_y, "Proposer:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(page_width - x_pos - c.stringWidth(title_data.get('proposer', ''), "Helvetica", 12), theme_y, f" {title_data.get('proposer', '')}")
        
        # Add minted and contributors information (third line)
        minted_text = f"Minted: {title_data.get('minted', 0)}"
        artists_text = f"Contributors: {title_data.get('artists', 0)}"
        
        # Position minted/contributors text below theme
        text_y = theme_y - 20  # 20 pixels below second line
        
        # Draw minted count (left-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        c.drawString(x_pos, text_y, "Minted:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(x_pos + c.stringWidth("Minted:", "Helvetica-Oblique", 12), text_y, f" {title_data.get('minted', 0)}")
        
        # Draw artists count (right-aligned)
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        artists_width = c.stringWidth("Contributors:", "Helvetica-Oblique", 12)
        c.drawString(page_width - x_pos - artists_width - c.stringWidth(str(title_data.get('artists', 0)), "Helvetica", 12), text_y, "Contributors:")
        c.setFont("Helvetica", 12)  # Regular font for the rest
        c.drawString(page_width - x_pos - c.stringWidth(str(title_data.get('artists', 0)), "Helvetica", 12), text_y, f" {title_data.get('artists', 0)}")
        
        # Add palette info (fourth line)
        pixel_counts = count_pixels(image_path, palette)
        palette_text = "Palette:"
        c.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
        c.drawString(x_pos, text_y - 20, palette_text)
        c.setFont("Helvetica", 12)  # Regular font for the rest
        palette_text_padding = c.stringWidth(palette_text, "Helvetica", 12)
        sorted_palette = sorted(zip(pixel_counts, palette), key=lambda x: x[0], reverse=True)
        for i, (count, color) in enumerate(sorted_palette):
            pixel_counts_text = f"  {count:.2f}% "
            c.drawString(
                x_pos + ((i) * square_spacing) + palette_text_padding,
                text_y - 20,
                pixel_counts_text)
            palette_text_padding += c.stringWidth(pixel_counts_text, "Helvetica", 12)
            c.setFillColorRGB(color[0]/255, color[1]/255, color[2]/255)
            c.setStrokeColorRGB(0, 0, 0)  # Set border color to black
            c.rect(x_pos + (i * square_spacing) + palette_text_padding,
                  text_y - 20, 
                  square_size, square_size,
                  fill=1, stroke=1)  # stroke=1 to draw the border
            # Reset fill color to black for subsequent text
            c.setFillColorRGB(0, 0, 0)
        # Add image
        c.drawImage(image_path,
                   x_pos,  # center horizontally
                   page_height - scaled_height - 70,  # position below title
                   width=scaled_width, 
                   height=scaled_height)
        
        # Add attribution footer
        footer_y_base = 40  # Base position from bottom of page
        line_spacing = 15  # Space between lines
        
        # First line - canvas URL
        c.setFont("Helvetica", 10)
        prefix_text = "Artwork generated collaboratively at "
        url_text = f"https://basepaint.xyz/canvas/{day_num}"
        
        prefix_width = c.stringWidth(prefix_text, "Helvetica", 10)
        c.setFont("Courier", 10)
        url_width = c.stringWidth(url_text, "Courier", 10)
        total_width = prefix_width + url_width
        
        start_x = (page_width - total_width) / 2
        c.setFont("Helvetica", 10)
        c.drawString(start_x, footer_y_base, prefix_text)
        c.setFont("Courier", 10)
        c.drawString(start_x + prefix_width, footer_y_base, url_text)
        
        # Second line - archive info
        c.setFont("Helvetica", 10)
        archive_prefix = "Archive available at "
        archive_url = "https://github.com/isaacbernat/basepaint"
        
        archive_prefix_width = c.stringWidth(archive_prefix, "Helvetica", 10)
        c.setFont("Courier", 10)
        archive_url_width = c.stringWidth(archive_url, "Courier", 10)
        total_archive_width = archive_prefix_width + archive_url_width
        
        start_archive_x = (page_width - total_archive_width) / 2
        c.setFont("Helvetica", 10)
        c.drawString(start_archive_x, footer_y_base - line_spacing, archive_prefix)
        c.setFont("Courier", 10)
        c.drawString(start_archive_x + archive_prefix_width, footer_y_base - line_spacing, archive_url)
        
        c.showPage()
    
    c.save()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "images")
    csv_path = os.path.join(script_dir, "metadata.csv")

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
