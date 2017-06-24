import helper
from image_processor import ImageProcessor
from file_info import FileInfo


class SortImagesToFolder(ImageProcessor):
    """
        Reads the exif data from files in a given folder and maps them to folders in a specified output folder.
    """

    def place_image_in_folder(self, sort_option, img_file_orig, file_info):
        data = file_info.data
        tag_keys = list(data.keys())
        tag_keys.sort()

        exif_date_fields = ['Image DateTime',
                            'EXIF DateTimeDigitized', 'EXIF DateTimeOriginal']

        key = helper.get_existing_exif_key(tag_keys)
        try:
            self.do_action(file_info, sort_option,
                           img_file_orig, key)
        except:
            self.incr_skipped()

    def do_action(self, file_info, sort_option, img_file_orig, key):
        date = helper.get_date_format(
            file_info.data, sort_option, key)
        self.write_image_to_folder(
            file_info['filename'], file_info['destination'], date, img_file_orig)

    def write_image_to_folder(self, filename, destination, date, img_file_orig):
        """ Writes image to given destination folder """
        if len(destination) > 0:
            helper.write_file(filename, destination + '/' +
                              date + '/', img_file_orig)
        else:
            helper.write_file(filename, date + '/', img_file_orig)
        super.write_image_to_folder(filename, destination, date, img_file_orig)
