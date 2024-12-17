import requests
import csv
import os
from typing import Dict, List, Any
from downloader import LATEST

def fetch_day_data(day: int) -> Dict[str, Any]:
    """Fetch data for a specific day from the BasePaint API."""
    url = f'https://basepaint.xyz/api/art/{hex(day)[2:]}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant metadata from the API response."""
    metadata = {
        'NUM': None,
        'TITLE': None,
        'ARTISTS': None,
        'PALETTE': None,
        'PROPOSER': None,
        'MINT_DATE': None
    }
    
    # Extract attributes
    for attr in data.get('attributes', []):
        if attr['trait_type'] == 'Day':
            metadata['NUM'] = int(attr['value'])
        elif attr['trait_type'] == 'Theme':
            metadata['TITLE'] = attr['value']
        elif attr['trait_type'] == 'Contributor Count':
            metadata['ARTISTS'] = attr['value']
        elif attr['trait_type'] == 'Proposer':
            metadata['PROPOSER'] = attr['value']
        elif attr['trait_type'] == 'Mint Date':
            metadata['MINT_DATE'] = attr['value']
        elif attr['trait_type'].startswith('Color #'):
            if metadata['PALETTE'] is None:
                metadata['PALETTE'] = []
            # Convert hex to RGB
            hex_color = attr['value'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            metadata['PALETTE'].append(f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
    
    if metadata['PALETTE']:
        metadata['PALETTE'] = ';'.join(metadata['PALETTE'])
    
    return metadata

def create_metadata_csv(max_day: int):
    """Create metadata.csv by fetching data for each day."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "metadata.csv")
    
    fieldnames = ['NUM', 'TITLE', 'PALETTE', 'MINTED', 'ARTISTS', 'PROPOSER', 'MINT_DATE']
    
    # Read existing days from CSV if it exists
    existing_days = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_days = {int(row['NUM']) for row in reader}
    
    # Open in append mode if file exists, write mode if it doesn't
    mode = 'a' if os.path.exists(csv_path) and existing_days else 'w'
    with open(csv_path, mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()
        
        for day in range(1, max_day + 1):
            if day in existing_days:
                print(f"Skipping Day {day}: Already in CSV")
                continue
                
            try:
                data = fetch_day_data(day)
                metadata = extract_metadata(data)
                
                # Set MINTED to 0 since it's not available in the API
                metadata['MINTED'] = 0
                
                if all(metadata[key] is not None for key in ['NUM', 'TITLE', 'ARTISTS']):
                    writer.writerow(metadata)
                    print(f"Processed Day {day}: {metadata['TITLE']}")
                else:
                    print(f"Skipping Day {day}: Incomplete data")
            except Exception as e:
                print(f"Error processing Day {day}: {str(e)}")

if __name__ == "__main__":
    create_metadata_csv(LATEST)
