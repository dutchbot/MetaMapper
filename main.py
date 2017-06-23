import os
import sys
import getopt
import helper
from exif_options import ExifOptions
from exifread import process_file, exif_log, __version__

LOGGER = exif_log.get_logger()


def main():

    folder = input("Give a folder containing images..\n")

    destination = input("Give a destination for the ordered folders..\n")

    answer = ''

    result = 0

    result, answer = get_sorting_option("Order by year? y/n \n", 2)

    result, answer = get_sorting_option(
        "Order by year and month? y/n \n", 1, answer, result)

    result, answer = get_sorting_option(
        "Order by year,month and day? y/n \n", 0, answer, result)

    mode, answer = get_sorting_option("Recursively ? y/n \n", 'r')

    sort_images_to_folder = SortImagesToFolder()
    sort_images_to_folder.execute(folder, destination, result, mode)


def get_sorting_option(question, res, prev_ans=None, prev_res=None):
    result = 0
    if prev_ans != None and prev_res != None:
        if prev_ans != 'n':  # stop followup
            return prev_res, 'y'
    while True:
        answer = input(question)
        if answer not in "yn":
            print("Enter y or n")
            continue
        if answer == 'y':
            result = res
            break
        else:
            break
    return result, answer


class SortImagesToFolder:
    """
        Reads the exif data from files in a given folder and maps them to folders in a specified output folder.
    """

    def __init__(self):
        self.writes = 0
        self.skipped = 0
        self.errors = 0
        self.no_exif = 0

    def execute(self, folder, destination, sort_option, mode):
        """ Execute the main function, limiting to known images with exif format."""
        # Relative or absolute path
        exif_opt = ExifOptions()
        if os.path.isdir(folder):
            count_files = 0

            if mode == 'r':
                for folder, subs, files in os.walk(folder):
                    count = 0
                    if destination not in subs:
                        for file in files:
                            if count == 0:
                                print(folder)
                                count += 1
                            if helper.check_file_extensions(file):
                                try:
                                    self.walk_images(file, folder, destination,
                                                     sort_option, exif_opt)
                                except:
                                    LOGGER.error("error on file! : " + file)
                                    self.incr_errors()
                                count_files += 1
                print('Found image files ' + str(count_files))
            else:
                files = [f for f in os.listdir(folder)
                         if helper.check_tiff_extension(file) or helper.check_jpeg_extension(file)]
                for file in files:
                    try:
                        self.walk_images(file, folder, destination,
                                         sort_option, exif_opt)
                    except:
                        print("error on file! : " + file)
                        self.incr_errors()
                    count_files += 1

            print('Processed image files ' + str(count_files))
            print('Skipped files ' + str(self.skipped))
            print('Error files ' + str(self.errors))
            print('Written ' + str(self.writes) + ' files')
        else:
            print('Invalid folder given')

    def walk_images(self, filename, folder, destination, sort_option, exif_options):

        img_file = open(str(folder + '/' + filename), 'rb')
        img_orig_writeback = open(str(folder + '/' + filename), 'rb')

        img_file_orig = img_orig_writeback.read()
        img_orig_writeback.close()

        try:
            # this process removes bytes, second buffer is a fix for this
            data = process_file(img_file)
        except UnicodeDecodeError:
            raise

        if not data:
            print(data)
            self.incr_skipped()
            return

        # removes the image thumbnail data (we dont need it)
        if 'JPEGThumbnail' in data:
            LOGGER.info('File has JPEG thumbnail')
            del data['JPEGThumbnail']
        if 'TIFFThumbnail' in data:
            LOGGER.info('File has TIFF thumbnail')
            del data['TIFFThumbnail']

        tag_keys = list(data.keys())
        tag_keys.sort()

        exif_date_fields = ['Image DateTime',
                            'EXIF DateTimeDigitized', 'EXIF DateTimeOriginal']

        if exif_date_fields[0] in tag_keys:
            date = helper.get_date_format(
                data, sort_option, exif_date_fields[0])
            self.write_image_to_folder(
                filename, destination, date, img_file_orig)
        elif exif_date_fields[1] in tag_keys:
            date = helper.get_date_format(
                data, sort_option, exif_date_fields[1])
            self.write_image_to_folder(
                filename, destination, date, img_file_orig)
        elif exif_date_fields[2] in tag_keys:
            date = helper.get_date_format(
                data, sort_option, exif_date_fields[2])
            self.write_image_to_folder(
                filename, destination, date, img_file_orig)
        else:
            self.incr_skipped()

    def write_image_to_folder(self, filename, destination, date, img_file_orig):
        """ Writes image to given destination folder """
        if len(destination) > 0:
            helper.write_file(filename, destination + '/' +
                              date + '/', img_file_orig)
            self.incr_writes()
        else:
            helper.write_file(filename, date + '/', img_file_orig)
            self.incr_writes()

    def incr_errors(self):
        self.errors += 1

    def incr_skipped(self):
        self.skipped += 1

    def incr_writes(self):
        self.writes += 1

if __name__ == '__main__':
    main()
