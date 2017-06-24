import argparse
from rename_image_prefix_date import RenameImagePrefixDate
from sort_images_to_folder import SortImagesToFolder


def main():

    args = parse_arguments()

    if args.mode == 'r':
        rename_image_prefix_date = RenameImagePrefixDate()
        print(args.prefix)
        print(args.output_path)
        sort_option = {'prefix': args.prefix, 'date_format': 0}
        rename_image_prefix_date.walk_images(
            args.input_path, args.output_path, sort_option, 'r')
    else:
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
        sort_images_to_folder.walk_images(folder, destination, result, mode)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Sort files on exif date info, or rename them.')
    parser.add_argument('-o', dest="output_path", action="store",
                        default="", help='The absolute directory to output the files to.')
    parser.add_argument('-i', dest="input_path", action="store", default=".",
                        help='the path to read input from, defaults to current folder')
    parser.add_argument('-mode', dest="mode", action="store", default="s",
                        help=" 's' => Sort, 'r' => Rename, default = Sort")
    parser.add_argument('--prefix', action="store",
                        dest="prefix", default="IMAGE", help='Default prefix is IMAGE e.g PREFIX_DATE -> IMAGE_20160111')
    parser.add_argument('--verbose', action="store_true",
                        dest="verbose", help='Display all actions')
    args = parser.parse_args()
    return args


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


if __name__ == '__main__':
    main()
