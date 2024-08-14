import pandas as pd
import os
import requests

input_folder = 'Path/to/all/filtered_csv'

# Donwload 1 photo
def download_photo(photo_id, extension):
    url = f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/medium.{extension}"
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(download_folder, f"{photo_id}.{extension}")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download photo {photo_id} with extension {extension}")

for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        download_folder = f'/Path/to/folder/to/save/photos/{filename}'
        os.makedirs(download_folder)
        input_file_path = os.path.join(input_folder, filename)

        # Read csv
        df = pd.read_csv(input_file_path)

        # download all photos from csv
        for index, row in df.iterrows():
            photo_id = row['photo_id']
            extension = row['extension']
            download_photo(photo_id, extension)

print("Downloaded all photos !")
