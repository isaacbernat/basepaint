import os
import csv
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image


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
                'MINT_DATE': row.get('MINT_DATE', ''),
            }
    return titles


def count_pixels(image_path, palette):
    image = Image.open(image_path).convert("RGB")  # Ensure image is in RGB mode
    pixel_count = [0] * len(palette)
    color_dict = {tuple(color): index for index, color in enumerate(palette)}
    for pixel in image.getdata():
        pixel_count[color_dict[pixel]] += 1
    return [(count / (image.width * image.height)) * 100 for count in pixel_count]  # percentage_count


def draw_text(canvas, text_italic, text_normal, x, y, italic_offset, x_offset, page_width):
    canvas.setFont("Helvetica-Oblique", 12)  # Italic for descriptive part
    canvas.drawString(x + x_offset, y, text_italic)
    canvas.setFont("Helvetica", 12)  # Regular font for the rest
    if italic_offset:
        total_italic_offset = x + x_offset + italic_offset
    else:
        total_italic_offset = page_width - canvas.stringWidth(text_normal) - x
    canvas.drawString(total_italic_offset, y, text_normal)


def draw_header(canvas, day_num, titles, x_pos, page_height, page_width):
    title_data = titles.get(day_num, {'title': '', 'palette': []})
    title = f"Day {day_num}: {title_data['title']}"
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(x_pos, page_height - 50, title)
    
    square_size = canvas.stringWidth("O", "Helvetica-Bold", 14)  # Size of capital O
    square_spacing = square_size * 1.2  # Add some spacing between squares
    palette = title_data['palette']
    total_palette_width = len(palette) * square_spacing
    start_x = page_width - x_pos - total_palette_width
    
    for i, color in enumerate(palette):
        canvas.setFillColorRGB(color[0]/255, color[1]/255, color[2]/255)
        canvas.rect(start_x + (i * square_spacing), page_height - 50 - square_size/2, 10, 10, fill=1, stroke=1)  # stroke=1 to draw the border
    canvas.setFillColorRGB(0, 0, 0)  # Reset fill color to black for subsequent text


def draw_footer_line(c, footer_y, page_width, prefix_text, url_text):
    prefix_width = c.stringWidth(prefix_text, "Helvetica", 10)
    total_width = prefix_width + c.stringWidth(url_text, "Courier", 10)
    start_x = (page_width - total_width) / 2

    c.setFont("Helvetica", 10)
    c.drawString(start_x, footer_y, prefix_text)
    c.setFont("Courier", 10)
    c.drawString(start_x + prefix_width, footer_y, url_text)


def draw_description(c, titles, day_num, pixel_counts, x_pos, page_width, first_line_y):
    formatted_mint_date = datetime.fromtimestamp(int(titles.get(day_num, {}).get('MINT_DATE', ''))).strftime('%Y-%m-%d')
    left_column_italic_offset = c.stringWidth("Mint date: ", "Helvetica-Oblique", 12)
    left_column = [("Mint date:", f" {formatted_mint_date}"),
                   ("Theme:", f" {titles.get(day_num, {}).get('title', '')}"),
                   ("Proposer:", f" {titles.get(day_num, {}).get('proposer', '')}"),
                   ("Palette:", ""),
    ]
    right_column = [("Day:", f" {day_num}"),
                    ("Minted:", f" {titles.get(day_num, {}).get('minted', 0)}"),
                    ("Artists:", f" {titles.get(day_num, {}).get('artists', 0)}"),
                    ("", ""),
    ]
    for i, (left_text, right_text) in enumerate(zip(left_column, right_column)):
        draw_text(c, left_text[0], left_text[1], x_pos, first_line_y - (i * 20), italic_offset=left_column_italic_offset, x_offset=0, page_width=page_width)
        draw_text(c, right_text[0], right_text[1], x_pos, first_line_y - (i * 20), italic_offset=0, x_offset=page_width * 0.75, page_width=page_width)
    
    palette_text_padding = left_column_italic_offset
    sorted_palette = sorted(zip(pixel_counts, titles.get(day_num, {}).get('palette', [])), key=lambda x: x[0], reverse=True)
    for i, (count, color) in enumerate(sorted_palette):
        pixel_counts_text = f" {count:.2f}% "
        c.drawString(x_pos + ((i) * 20) + palette_text_padding, first_line_y - 60, pixel_counts_text)
        c.setFont("Courier", 12)
        c.drawString(x_pos + ((i) * 20) + palette_text_padding, first_line_y - 80, f" #{color[0]:02x}{color[1]:02x}{color[2]:02x}")
        c.setFont("Helvetica", 12)
        palette_text_padding += c.stringWidth(pixel_counts_text, "Helvetica", 12)
        c.setFillColorRGB(color[0] / 255, color[1] / 255, color[2] / 255)
        c.rect(x_pos + (i * 20) + palette_text_padding, first_line_y - 60, 10, 10, fill=1, stroke=1)  # stroke=1 to draw the border
        c.setFillColorRGB(0, 0, 0)  # Reset fill color to black for subsequent text


def create_pdf_from_images(input_directory, output_pdf, titles, image_files):
    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setStrokeColorRGB(0, 0, 0)  # Set border color to black
    page_width, page_height = A4
    img_size = 2560 * 72 / 96  # Convert pixels to points (96 DPI to 72 DPI)
    scale_factor = (page_width * 0.9) / img_size  # 90% of page width
    scaled_width = scaled_height = img_size * scale_factor
    x_pos = (page_width - scaled_width) / 2
    
    print("Creating PDF...")
    for page_num, image_file in enumerate(image_files, 1):  # Process each image
        day_num = int(image_file.split('.')[0])  # Extract day number (assuming XXXX.jpg)
        if page_num % 12 == 0:
            print(f"Processing image {day_num}")
            break
        draw_header(c, day_num, titles, x_pos, page_height, page_width)
        image_path = os.path.join(input_directory, image_file)
        c.drawImage(image_path,
                   x_pos,  # center horizontally
                   page_height - scaled_height - 70,  # position below header
                   width=scaled_width, 
                   height=scaled_height)
        pixel_counts = count_pixels(image_path, titles.get(day_num, {}).get('palette', []))
        draw_description(c, titles, day_num, pixel_counts, x_pos, page_width, first_line_y=(page_height - scaled_height - 90))
        draw_footer_line(c, 40, page_width, "Artwork generated collaboratively at ", f"https://basepaint.xyz/canvas/{day_num}")
        draw_footer_line(c, 40 - 15, page_width, "Archive available at ", "https://github.com/isaacbernat/basepaint")
        c.showPage()
    c.save()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "images")
    titles = load_titles(os.path.join(script_dir, "metadata.csv"))
    image_files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith('.jpg')])
    last_day = len(image_files)
    output_pdf = os.path.join(script_dir, f"basepaint_until_{last_day:04d}.pdf")
    create_pdf_from_images(img_dir, output_pdf, titles, image_files)
    print(f"PDF has been created: {output_pdf}")
