import os
import sys
import getopt
import helper
from file_info import FileInfo
from exif_options import ExifOptions
from exifread import process_file, exif_log, __version__

LOGGER = exif_log.get_logger()


class ImageProcessor:

    def __init__(self):
        self.writes = 0
        self.skipped = 0
        self.errors = 0
        self.no_exif = 0

    def walk_images(self, folder, destination, sort_option, mode):
        """ Execute the main function, limiting to known images with exif format."""
        # Relative or absolute path
        exif_opt = ExifOptions()
        if os.path.isdir(folder):
            count_files = 0

            if mode == 'r':
                for folder, subs, files in os.walk(folder):
                    count = 0
                    if destination not in subs:
                        for file_name in files:
                            if count == 0:
                                print(folder)
                                count += 1
                            if helper.check_file_extensions(file_name):
                                try:
                                    self.process_image(
                                        FileInfo(file_name, folder, destination), sort_option)
                                except:
                                    LOGGER.error(
                                        "error on file! : " + file_name)
                                    self.incr_errors()
                                count_files += 1
                print('Found image files ' + str(count_files))
            else:
                files = [f for f in os.listdir(folder)
                         if helper.check_tiff_extension(file_name) or helper.check_jpeg_extension(file_name)]
                for file_name in files:
                    try:
                        self.process_image(
                            FileInfo(file_name, folder, destination), sort_option)
                    except:
                        print("error on file! : " + file_name)
                        self.incr_errors()
                    count_files += 1

            print('Processed image files ' + str(count_files))
            print('Skipped files ' + str(self.skipped))
            print('Error files ' + str(self.errors))
            print('Written ' + str(self.writes) + ' files')
        else:
            print('Invalid folder given')

    def process_image(self, file_info, sort_option):
        """
            Read the image exif contents and write it somewhere.
        """
        folder = file_info.current_folder
        filename = file_info.filename

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
            # print(data)
            self.incr_skipped()
            return

        self.remove_image_thumbnail(data)
        file_info.data = data
        self.place_image_in_folder(sort_option, img_file_orig, file_info)

    def place_image_in_folder(self, sort_option, img_file_orig, file_info):
        pass

    def remove_image_thumbnail(self, data):
        """
            removes the image thumbnail data
        """
        if 'JPEGThumbnail' in data:
            LOGGER.info('File has JPEG thumbnail')
            del data['JPEGThumbnail']
        if 'TIFFThumbnail' in data:
            LOGGER.info('File has TIFF thumbnail')
            del data['TIFFThumbnail']

    def write_image_to_folder(self, filename, destination, date, img_file_orig):
        self.incr_writes()

    def incr_errors(self):
        self.errors += 1

    def incr_skipped(self):
        self.skipped += 1

    def incr_writes(self):
        self.writes += 1
