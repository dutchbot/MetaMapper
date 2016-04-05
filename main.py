import sys
import getopt
import logging
import timeit
import os
import copy
from dateutil.parser import parse
from exifread.tags import DEFAULT_STOP_TAG, FIELD_TYPES
from exifread import process_file, exif_log, __version__

logger = exif_log.get_logger()

def main():

    folder = input("Give an folder containing images..\n")
     
    folder = './' + folder
     
    destination = input("Give an destination for the ordered folders..\n")

    year = ''

    result = 0

    result,year = get_sorting_option("Order by year? y/n \n",2)

    result,year = get_sorting_option("Order by year and month? y/n \n",1,year,result)

    result,year = get_sorting_option("Order by year,month and day? y/n \n",0,year,result)

    execute(folder,destination,result)

def get_sorting_option(question,res,prev_ans= None,prev_res = None):
    result = 0
    if prev_ans != None and prev_res != None:
        if prev_ans != 'n': #stop followup
            return prev_res,'y'
    while True:  
        year = input(question)
        if year not in "yn":
            print("Enter y or n")    
            continue
        if year == 'y':
            result = res
            break
        else:
            break
    return result,year
        
def execute(folder, destination, sort_option):

    print(sort_option)
    
    if os.path.isdir(folder):
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1] == '.jpg']
        detailed = False
        stop_tag = DEFAULT_STOP_TAG
        debug = False
        strict = False
        color = False
        dates = {}
        count = 0

        print('Found jpg files ' + str(len(files)))
        
        for filename in files:
            file_start = timeit.default_timer()
            
            try:
                img_file = open(str(folder+'/'+filename), 'rb')
                img_orig_writeback = open(str(folder+'/'+filename), 'rb') # i dont like it but easiest fix
            except IOError:
                logger.error("'%s' is unreadable", filename)
                continue
            
            logger.info("Opening: %s", filename)

            tag_start = timeit.default_timer()
            
            img_file_orig = img_orig_writeback.read()
            file_name = str(img_file_orig)[29:][:-2]

            try:
                # this process removes bytes, second buffer is a fix for this
                data = process_file(img_file, stop_tag=stop_tag, details=detailed, strict=strict, debug=debug)
            except UnicodeDecodeError:
                continue

            tag_stop = timeit.default_timer()

            if not data:
                logger.info("No EXIF information found\n")
                continue

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
                count+=1
                print(data['Image DateTime'].printable)
                
                s = data['Image DateTime'].printable
                fixed_date = s.replace(":","-",2)

                date = str((parse(fixed_date).date()))
                if sort_option == 1: # year and month
                   date = date[:-3]
                elif sort_option == 2: # year
                   date = date[:-6]
                    
                if dates.get(date) == None:
                    dates[date] = {filename:img_file_orig}
                else:
                    # add the data to the existing key
                    dates.get(date)[filename]=img_file_orig
                
                logger.info(data['Image DateTime'].printable)

            file_stop = timeit.default_timer()

            logger.debug("Tags processed in %s seconds", tag_stop - tag_start)
            logger.debug("File processed in %s seconds", file_stop - file_start)
            
        print('Processed jpg files ' + str(count))
        
        for date in dates:
            
            make_sure_path_exists("./"+date)
            
            for filename,file in dates.get(date).items():
                
                print(sys.getsizeof(file))
                if len(destination) > 0:
                    write_file(filename,destination+'/'+date+'/',file)
                else:
                    write_file(filename,date+'/',file)
                
            print(str(date))
    else:
        print('Invalid folder given')

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