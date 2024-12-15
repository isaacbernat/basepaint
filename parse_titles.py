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
                
                # Find stats div for minted and artists counts
                stats_div = div.find_next('div', class_='hidden sm:block text-sm text-gray-400')
                minted_count = 0
                artists_count = 0
                if stats_div:
                    stats_text = stats_div.text.strip()
                    minted_match = re.search(r'(\d+) minted', stats_text)
                    artists_match = re.search(r'(\d+) artists', stats_text)
                    if minted_match:
                        minted_count = int(minted_match.group(1))
                    if artists_match:
                        artists_count = int(artists_match.group(1))
                
                # Find the color palette div that follows this title
                palette_div = div.find_next('div', class_='inline-flex flex-row gap-0.5 pt-0.5 items-start')
                colors = []
                if palette_div:
                    color_divs = palette_div.find_all('div', class_='w-4 h-4 sm:block hidden border border-1 border-gray-700 rounded-sm')
                    for color_div in color_divs:
                        style = color_div.get('style', '')
                        color_match = re.search(r'background-color: rgb\((.*?)\)', style)
                        if color_match:
                            colors.append(color_match.group(1))
                
                # Join colors with semicolon for CSV storage
                palette = ';'.join(colors) if colors else ''
                entries.append((int(num), title.strip(), palette, minted_count, artists_count))  # Add new stats
        
        # Sort entries by number
        entries.sort(key=lambda x: x[0])
        
        # Write sorted entries to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvf:
            writer = csv.writer(csvf)
            writer.writerow(['NUM', 'TITLE', 'PALETTE', 'MINTED', 'ARTISTS'])  # Add new columns
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
