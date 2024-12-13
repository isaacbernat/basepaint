from bs4 import BeautifulSoup
import os
import csv
import re


# prerreq, download https://basepaint.xyz/gallery as gallery.html first
def parse_gallery_titles(html_file, csv_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find all div elements and store them in a list for sorting
        title_divs = soup.find_all('div', class_='sm:flex-1 text-white text-md')
        entries = []
        
        for div in title_divs:
            text = div.text.strip()
            match = re.match(r'Day #(\d+): (.*)', text)
            if match:
                num, title = match.groups()
                entries.append((int(num), title.strip()))  # Convert num to int for proper sorting
        
        # Sort entries by number
        entries.sort(key=lambda x: x[0])
        
        # Write sorted entries to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvf:
            writer = csv.writer(csvf)
            writer.writerow(['NUM', 'TITLE'])  # Write header
            writer.writerows(entries)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gallery_path = os.path.join(script_dir, "gallery.html")
    csv_path = os.path.join(script_dir, "gallery_titles.csv")
    
    if not os.path.exists(gallery_path):
        print(f"Error: {gallery_path} not found")
        exit(1)
        
    parse_gallery_titles(gallery_path, csv_path)
    print(f"CSV file created: {csv_path}")
