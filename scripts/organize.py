import os
import PIL.Image
import shutil
import argparse

from datetime import datetime

IMAGE_EXTENSIONS = [ '.jpg' ]
REVIEW_DIR = '0000000'

def get_creation_date_from_meta_data(file_path):
    valid_image_date_tags = [ 36867, 36868 ] # DateTimeOriginal, DateTimeDigitized
    image_date_time = None

    img = PIL.Image.open(file_path)
    exif_data = img._getexif()

    for tag in valid_image_date_tags:
            try:
                image_date_time_str = exif_data[tag]

                image_date_time = datetime.strptime(image_date_time_str, '%Y:%m:%d %H:%M:%S')
                break
            except:
                continue

    return image_date_time

def get_creation_date_from_file_data(file_path):
    created = os.path.getctime(file_path)
    last_modified = os.path.getmtime(file_path)

    return datetime.fromtimestamp(min(created, last_modified))

def get_file_date(file_path):
    file_date = None
    file_name, file_extension = os.path.splitext(file_path)

    if (file_extension.lower() in IMAGE_EXTENSIONS):
            # first, try to read image taken date from exif
            try:
                    file_date = get_creation_date_from_meta_data(file_path)
            except:
                    print(f'{file_path}: Couldn\'t open the file.')

            if (file_date == None):
                    print(f'{file_path}: Could\'t read image taken date.')
                    file_date = get_creation_date_from_file_data(file_path)
    else:
            # it's not an image, get file creation date
            file_date = get_creation_date_from_file_data(file_path)

    return file_date

def move_file(source_file, destination_file):
    # create destination folder
    os.makedirs(os.path.dirname(destination_file), exist_ok=True)

    # move the file
    shutil.move(source_file, destination_file)

def organize(source_dir, target_dir):
    for f in os.listdir(source_dir):
            file_path = os.path.join(source_dir, f)

            if (os.path.isfile(file_path)):
                    file_date = get_file_date(file_path)

                    year_dir = str(file_date.year)
                    file_dir = '{d.month}-{d.day}-{d.year}'.format(d=file_date)

                    target_file_path = os.path.join(target_dir, year_dir, file_dir, f)

                    if (os.path.isfile(target_file_path)):
                            # file exists, move it to "review" folder instead
                            print(f'{file_path}: Already exists. {target_file_path}')
                            target_file_path = os.path.join(target_dir, REVIEW_DIR, year_dir, file_dir, f)

                    #move_file(file_path, target_file_path)
                    print(f'{file_path}: Moved to {target_file_path}.')
            else:
                    organize(file_path, target_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Organize files into folders automatically based on date created. Format: {year}/{month}-{day}-{year}')

    parser.add_argument('source_dir', type=str, help='Source directory')
    parser.add_argument('destination_dir', type=str, help='Destination directory')

    args = parser.parse_args()

    organize(args.source_dir, args.destination_dir)