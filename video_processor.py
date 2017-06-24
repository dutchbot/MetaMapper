import os
import helper
import logging
import datetime
from file_info import FileInfo

MP4 = '.mp4'
LOGGER = logging.getLogger()


class VideoProcessor():

    def __init__(self):
        self.writes = 0
        self.skipped = 0
        self.errors = 0
        self.no_exif = 0

    def scan_files(self, folder, destination, sort_option, mode):
        # Relative or absolute path
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
                            if helper.check_extension(file_name, MP4):
                                try:
                                    self.process_file(
                                        FileInfo(file_name, folder, destination), sort_option)
                                except:
                                    raise
                                    LOGGER.error(
                                        "error on file! : " + file_name)
                                    self.incr_errors()
                                count_files += 1
                print('Found video files ' + str(count_files))
            else:
                files = [f for f in os.listdir(folder)
                         if helper.check_extension(file_name, MP4) or helper.check_jpeg_extension(file_name)]
                for file_name in files:
                    try:
                        self.process_file(
                            FileInfo(file_name, folder, destination), sort_option)
                    except:
                        print("error on file! : " + file_name)
                        self.incr_errors()
                    count_files += 1

    def process_file(self, file_info, sort_option):
        """
            Look at the modified time
        """
        video_orig_writeback = open(
            str(file_info.current_folder + '/' + file_info.filename), 'rb')

        video_file_orig = video_orig_writeback.read()
        video_orig_writeback.close()

        time = os.path.getmtime(
            file_info.current_folder + "\\" + file_info.filename)
        date = datetime.datetime.fromtimestamp(
            time).strftime('%Y-%m-%d %H:%M:%S')
        file_name = helper.create_filename_for_file(
            sort_option, MP4[1:], date)
        helper.write_file(file_name, file_info.destination + "\\", video_file_orig)
        self.incr_writes()

    def incr_errors(self):
        self.errors += 1

    def incr_skipped(self):
        self.skipped += 1

    def incr_writes(self):
        self.writes += 1
