import os
import shutil
import argparse
from datetime import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config

IMAGE_EXTENSIONS = ['.jpg', '.png']
REVIEW_DIR = '0000000'

def get_creation_date_from_meta_data(file_path):
	meta_date = None

	parser = createParser(file_path)

	if parser:
		with parser:
			try:
				valid_date_tags = ['date_time_original', 'creation_date']

				metadata = extractMetadata(parser)
				for tag in valid_date_tags:
					if metadata.has(tag):
						meta_date = metadata.get(tag)
						break
			except:
				pass

	return meta_date

def get_creation_date_from_file_data(file_path):
    created = os.path.getctime(file_path)
    last_modified = os.path.getmtime(file_path)

    return datetime.fromtimestamp(min(created, last_modified))

def get_file_date(file_path):
	file_date = None
	file_name, file_extension = os.path.splitext(file_path)

	# first, try to read media taken date from exif
	try:
		if (file_extension.lower() in IMAGE_EXTENSIONS):
			file_date = get_creation_date_from_meta_data(file_path)
	except:
	        print(f'{file_path}: Could\'t read media creation date.')

	if (file_date == None):
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

                    move_file(file_path, target_file_path)
                    print(f'{file_path}: Moved to {target_file_path}.')
            else:
                    organize(file_path, target_dir)


if __name__ == "__main__":
	config.quiet = True

	parser = argparse.ArgumentParser(description='Organize files into folders automatically based on date created. Format: {year}/{month}-{day}-{year}')

	parser.add_argument('source', type=str, help='Source directory')
	parser.add_argument('destination', type=str, help='Destination directory')

	args = parser.parse_args()
	organize(args.source, args.destination)