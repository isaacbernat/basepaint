from fetch_images import fetch_images
from fetch_metadata import create_metadata_csv
from enrich_metadata import enrich_metadata_csv
from image_to_pdf import create_pdf
LATEST = 556


if __name__ == '__main__':
    print(f"Creating archive for up to day {LATEST}.")
    fetch_images(LATEST)
    create_metadata_csv(LATEST)
    enrich_metadata_csv()
    create_pdf()
