import os
import constant
from dateutil.parser import parse


def get_date_format(data, sort_option, field):
    date_string = data[field].printable
    fixed_date = date_string.replace(":", "-", 2)

    date = str(parse(fixed_date).date())
    if sort_option == 1:  # year and month
        date = date[:-3]
    elif sort_option == 2:  # year
        date = date[:-6]

    return date


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def write_file(filename, path, data):
    make_sure_path_exists(path)
    file_buffer = open(path + filename, "wb")
    file_buffer.write(data)
    file_buffer.close()


def check_file_extensions(file):
    """ Check for files which may hold exif data """
    if check_tiff_extension(file):
        return True
    elif check_jpeg_extension(file):
        return True
    return False


def check_tiff_extension(file):
    """ Check tiff ext """
    if get_file_ext(file) == constant.types[0] or get_file_ext(file) == constant.types[1]:
        return True
    return False


def check_jpeg_extension(file):
    """ Check jpeg ext """
    if get_file_ext(file) == constant.types[2] or get_file_ext(file) == constant.types[3]:
        return True
    return False


def get_file_ext(file):
    """ Return the file extension """
    return os.path.splitext(file)[1]
