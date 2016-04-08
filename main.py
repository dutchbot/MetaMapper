import sys
import getopt
import logging
import os
from dateutil.parser import parse
from exifread.tags import DEFAULT_STOP_TAG, FIELD_TYPES
from exifread import process_file, exif_log, __version__

logger = exif_log.get_logger()
writes = 0
skipped = 0
errors = 0
no_exif = 0

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
                count = 0
                if destination not in subs:
                    for file in files:
                        if(count == 0):
                            print(folder)
                            count+=1
                        if os.path.splitext(file)[1] == '.tif' or os.path.splitext(file)[1] == '.tiff' or os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.jpeg':
                            try:
                                walk_images(file, folder, destination, sort_option, exif_options)
                            except:
                                logger.error("error on file! : " + file)
                                incr_error()
                            count_files += 1
            print('Found image files ' + str(count_files))
        else:
            files = [f for f in os.listdir(folder) if os.path.splitext(f)[1] == '.tif' or os.path.splitext(f)[1] == '.tiff' or os.path.splitext(f)[1] == '.jpg' or os.path.splitext(f)[1] == '.jpeg']
            for file in files:
                try:
                    walk_images(file, folder, destination, sort_option, exif_options)
                except:
                    print("error on file! : " + file)
                    incr_error()
                count_files += 1
        
        print('Processed image files ' + str(count_files))
        print('Skipped files '  + str(skipped))
        print('Error files '  + str(errors))
        print('Written ' + str(writes) + ' files')   
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
        raise

    if not data:
        incr_skipped()
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
    
    exif_date_fields = ['Image DateTime','EXIF DateTimeDigitized','EXIF DateTimeOriginal']

    if exif_date_fields[0] in tag_keys:
        date = get_date_format(data, sort_option, exif_date_fields[0])
        write_image_to_folder(filename,destination,date,img_file_orig)
    elif exif_date_fields[1] in tag_keys:
        date = get_date_format(data, sort_option, exif_date_fields[1])
        write_image_to_folder(filename,destination,date,img_file_orig)
    elif exif_date_fields[2] in tag_keys:
        date = get_date_format(data, sort_option, exif_date_fields[2])
        write_image_to_folder(filename,destination,date,img_file_orig)
    else:
        incr_skipped()
       # print("Skipped " + filename + "\n")
        
def write_image_to_folder(filename, destination, date, img_file_orig):
   if len(destination) > 0:
      write_file(filename,destination+'/'+date+'/',img_file_orig)
      incr_writes()
   else:
      write_file(filename,date+'/',img_file_orig)
      incr_writes()

def incr_writes():
    global writes 
    writes += 1
    
def incr_skipped():
    global skipped
    skipped += 1

def incr_error():
    global errors
    errors += 1

def get_date_format(data, sort_option, field):
    s = data[field].printable
    fixed_date = s.replace(":","-",2)

    date = str(parse(fixed_date).date())
    if sort_option == 1: # year and month
       date = date[:-3]
    elif sort_option == 2: # year
       date = date[:-6]
    
    return date

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
