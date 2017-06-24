from image_processor import ImageProcessor
import helper


class RenameImagePrefixDate(ImageProcessor):
    """
        Reads the exif data from files in a given folder and rewrites them to PREFIX_DATE.ext
    """

    def place_image_in_folder(self, sort_option, img_file_orig, file_info):
        data = file_info.data
        tag_keys = list(data.keys())
        tag_keys.sort()

        key = helper.get_existing_exif_key(tag_keys)
        ext = file_info.filename.split('.')[1]
        filename = helper.create_filename_for_file(data, sort_option, ext, key)

        helper.write_file(filename, file_info.destination+"/", img_file_orig)
