#!/usr/bin/env python3

import argparse
import json

import dateutil.parser


def load(file):
    list_of_files = []

    with open(file) as file_pointer:
        for line in file_pointer:
            print(line)
            list_of_files.append(json.loads(line))

    return list_of_files


def file_is_in_list(source_file, destination_dictionary):
    source_file_path = source_file['Path']
    if source_file['Path'] not in destination_dictionary.keys():
        # No file with the same name: early exit
        return False

    destination_file = destination_dictionary[source_file_path]

    source_file_date = dateutil.parser.parse(source_file['ModTime'])
    source_file_size = source_file['Size']

    destination_file_date = dateutil.parser.parse(destination_file['ModTime'])
    destination_file_size = destination_file['Size']

    if (source_file_date - destination_file_date).seconds > 2:
        return False

    if source_file_size != destination_file_size:
        ratio = destination_file_size / source_file_size

        if ratio < 1:
            # Files don't seem to get smaller
            return False

        if source_file_size > 50 * 1024 and destination_file_size / source_file_size > 1.5:
            # Too big!
            return False

    return True


def load_files(file_path):
    file_dictionary = {}

    with open(file_path) as file:
        files = json.load(file)

        for file in files:
            if file['IsDir']:
                continue

            file_dictionary[file['Path']] = file

    return file_dictionary


def check_files(source_file, destination_file, output_file):
    source_files = load_files(source_file)
    destination_files = load_files(destination_file)

    missing_files = []

    for source_file in source_files.values():
        if not file_is_in_list(source_file, destination_files):
            missing_files.append(source_file)

    print('Total files in source:', len(source_files))
    print('Total files in destination:', len(destination_files))
    print('Total missing files:', len(missing_files))

    for missing_file in missing_files:
        print(missing_file)


def main():
    parser = argparse.ArgumentParser(
        description="Writes to OUTPUT the files in the SOURCE file list but not in the DESTINATION file list. Based on datetime (less than 2 secs) and filesize (fuzzy as well)")
    parser.add_argument("source",
                        help="Source file: containing a list of original files in rclone JSON format (rclone lsjson)")
    parser.add_argument("destination", help="Destination file: containing a list of destination files (rclone lsjson)")
    parser.add_argument("output", help="Output file with the missing files in [DESTINATION] from [SOURCE]")

    args = parser.parse_args()

    check_files(args.source, args.destination,
                args.output)


if __name__ == "__main__":
    main()
