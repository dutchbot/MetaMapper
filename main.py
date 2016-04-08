import sys
import getopt
import logging
import os
from dateutil.parser import parse
from exifread.tags import DEFAULT_STOP_TAG, FIELD_TYPES
from exifread import process_file, exif_log, __version__

logger = exif_log.get_logger()

class exif_options:
    detailed = False
    stop_tag = DEFAULT_STOP_TAG
    debug = False
    strict = False
    color = False

def main():

    folder = input("Give a folder containing images..\n")
     
    folder = './' + folder
     
    destination = input("Give a destination for the ordered folders..\n")

    answer = ''

    result = 0

    result, answer = get_sorting_option("Order by year? y/n \n", 2)

    result, answer = get_sorting_option("Order by year and month? y/n \n", 1, answer, result)

    result, answer = get_sorting_option("Order by year,month and day? y/n \n", 0, answer, result)

    mode, answer = get_sorting_option("Recursively ? y/n \n",'r')

    execute(folder,destination,result, mode)

def get_sorting_option(question,res,prev_ans= None,prev_res = None):
    result = 0
    if prev_ans != None and prev_res != None:
        if prev_ans != 'n': #stop followup
            return prev_res,'y'
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
    return result,answer
        
def execute(folder, destination, sort_option, mode):
    
    if os.path.isdir(folder):
        count_files = 0
    
        if mode == 'r':
            for folder, subs, files in os.walk(folder):
                for file in files:
                    if os.path.splitext(file)[1] == '.tif' or os.path.splitext(file)[1] == '.tiff'or os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.jpeg':
                        walk_images(file, folder, destination, sort_option, exif_options)
                        count_files += 1
            print('Found image files ' + str(count_files))
        else:
            files = [f for f in os.listdir(folder) if os.path.splitext(f)[1] == '.tif' or os.path.splitext(f)[1] == '.tiff' or os.path.splitext(f)[1] == '.jpg' or os.path.splitext(f)[1] == '.jpeg']
            for file in files:
                walk_images(file, folder, destination, sort_option, exif_options)
                count_files += 1
        
        print('Processed image files ' + str(count_files))   
    else:
        print('Invalid folder given')

def walk_images(filename, folder, destination, sort_option, exif_options):
    
    img_file = open(str(folder+'/'+filename), 'rb')
    img_orig_writeback = open(str(folder+'/'+filename), 'rb') # i dont like it but easiest fix
    
    img_file_orig = img_orig_writeback.read()
    img_orig_writeback.close()

    try:
        # this process removes bytes, second buffer is a fix for this
        data = process_file(img_file, stop_tag=exif_options.stop_tag, details=exif_options.detailed, strict=exif_options.strict, debug=exif_options.debug)
    except UnicodeDecodeError:
        print("unicode error")

    if not data:
        logger.info("No EXIF information found\n")
        return

    # removes the image thumbnail data (we dont need it)
    if 'JPEGThumbnail' in data:
        logger.info('File has JPEG thumbnail')
        del data['JPEGThumbnail']
    if 'TIFFThumbnail' in data:
        logger.info('File has TIFF thumbnail')
        del data['TIFFThumbnail']

    tag_keys = list(data.keys())
    tag_keys.sort()

    if 'Image DateTime' in tag_keys:
        
        s = data['Image DateTime'].printable
        fixed_date = s.replace(":","-",2)

        date = str((parse(fixed_date).date()))
        if sort_option == 1: # year and month
           date = date[:-3]
        elif sort_option == 2: # year
           date = date[:-6]
            
        if len(destination) > 0:
            write_file(filename,destination+'/'+date+'/',img_file_orig)
        else:
            write_file(filename,date+'/',img_file_orig)


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

def write_file(filename,path,data):
    make_sure_path_exists(path)
    f = open(path+filename,"wb")
    f.write(data)
    f.close()

if __name__ == '__main__':
    main()
