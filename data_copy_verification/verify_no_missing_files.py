#!/usr/bin/env python3

import argparse
import sys
import collections


def abort_if_line_incorrect(line, file_path, line_number):
    if line.count("\t") != 2:
        print("File path: {} Line Number: {} Not having 2 tabs".format(file_path, line_number), file=sys.stderr)
        print("Line: {}".format(line), file=sys.stderr)
        sys.exit(1)


def ignore_file(name, size):
    """ returns True if the file was not copied on purpose.

    Certain file names were not copied from the NAS to the object storage.
    """
    base_file_name = name.split("/")[-1]
    return size == 0 or "@eaDir/" in name or \
        base_file_name.startswith(".") or \
        base_file_name == "Thumbs.db" or \
        base_file_name == "desktop.ini" or \
        base_file_name.startswith("~") or \
        base_file_name.startswith("$")


def read_files_file(file_path, prefix_filter_and_ignore, include_all):
    if prefix_filter_and_ignore is None:
        prefix_filter_and_ignore = ""

    with open(file_path, mode="r", newline="\n") as f:
        file_sizes_etags = {}
        lines = set()

        line_number = 1

        SizeEtag = collections.namedtuple("size_etag", ["size", "etag"])

        for line in f.readlines():
            line = line.strip()

            abort_if_line_incorrect(line, file_path, line_number)

            if not line.startswith(prefix_filter_and_ignore):
                continue

            line = line[len(prefix_filter_and_ignore):]

            abort_if_line_incorrect(line, file_path, line_number)

            lines.add(line)

            (file_name, size, file_etag) = line.split("\t")

            if include_all or not etag_is_hash(file_etag):
                size_etag = SizeEtag(int(size), file_etag)

                file_sizes_etags[file_name] = size_etag

            line_number += 1

        return lines, file_sizes_etags


def etag_is_hash(etag):
    return "-" not in etag


def file_exists_name_size(file_name, size, etag, file_list):
    if file_name in file_list and file_list[file_name].size == size and \
            not (etag_is_hash(file_list[file_name].etag) and etag_is_hash(etag)):
        return True

    return False


def check_files(source, source_prefix_filter_and_strip, destination, destination_prefix_filter_and_strip, output_file_path):
    # Load source file
    (origin_files, origin_files_incomplete_etags) = read_files_file(source, source_prefix_filter_and_strip, include_all=False)
    (destination_files, all_destination_files_size_etags) = read_files_file(destination, destination_prefix_filter_and_strip, include_all=True)

    print("Origin files     :", len(origin_files))
    print("Destination files:", len(destination_files))

    count = 0

    output_file = open(output_file_path, "w")

    missing_files_count = 0

    for origin_file in origin_files:
        file_in_destination = origin_file in destination_files

        if not file_in_destination:
            (name, size, file_etag) = origin_file.split("\t")
            size = int(size)

            if ignore_file(name, size):
                continue

            file_name_exists = file_exists_name_size(name, size, file_etag, all_destination_files_size_etags)
            if not file_name_exists:
                output_file.write(origin_file + "\n")
                missing_files_count += 1

        count += 1
        if count % 10000 == 0:
            print("Done {} of {}".format(count, len(origin_files)))

    output_file.close()

    print("Source file: {} / Prefix filter+strip: {} ".format(source, source_prefix_filter_and_strip))
    print("Destination file: {} / Prefix filter+strip: {}".format(destination, destination_prefix_filter_and_strip))

    print("Finished - Missing files: {}. See output at: {}".format(missing_files_count, output_file_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source files: will check that all these files are in file2")
    parser.add_argument("destination", help="Destination files: will check that contains all the source files")
    parser.add_argument("output", help="Output file with the results")
    parser.add_argument("--source-prefix-filter-and-strip", help="Will read only source files starting with the given prefix AND will remove the prefix in the generated list")
    parser.add_argument("--destination-prefix-filter-and-strip", help="Will read only destination files starting with the given prefix AND will remove the prefix in the generated list")

    args = parser.parse_args()

    check_files(args.source, args.source_prefix_filter_and_strip,
                args.destination, args.destination_prefix_filter_and_strip,
                args.output)


if __name__ == "__main__":
    main()
