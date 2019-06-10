#!/usr/bin/env python3

import argparse
import sys
import collections
import os


def namedTupleFile():
    return collections.namedtuple("file", ["path", "size", "etag"])


def namedTupleSizeEtag():
    return collections.namedtuple("size_etag", ["size", "etag"])


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


def remove_path(file):
    Result = namedTupleFile()

    result = Result(os.path.basename(file.path), file.size, file.etag)

    return result


def read_files_file(data_file_path, prefix_filter_and_ignore, include_all, generate_file_name_only):
    if prefix_filter_and_ignore is None:
        prefix_filter_and_ignore = ""

    with open(data_file_path, mode="r", newline="\n") as f:
        file_sizes_etags_full_path = {}
        file_sizes_etags_only_names = {}

        all_files_full_path = set()
        all_files_only_names = set()

        line_number = 1

        File = namedTupleFile()
        SizeEtag = namedTupleSizeEtag()

        for line in f.readlines():
            if line_number % 10000 == 0:
                print("Reading: {} Line number: {} current file: {}".format(data_file_path, line_number, line.split("\t")[0]))

            line = line.strip()

            abort_if_line_incorrect(line, data_file_path, line_number)

            if not line.startswith(prefix_filter_and_ignore):
                continue

            line = line[len(prefix_filter_and_ignore):]

            abort_if_line_incorrect(line, data_file_path, line_number)

            (file_path, file_size, file_etag) = line.split("\t")

            file_size = int(file_size)
            file = File(file_path, file_size, file_etag)

            all_files_full_path.add(file)

            if generate_file_name_only:
                file_name_without_path = os.path.basename(file.path)

                all_files_only_names.add(File(file_name_without_path, file_size, file_etag))

            if include_all or not etag_is_hash(file.etag):
                size_etag = SizeEtag(file.size, file.etag)
                file_sizes_etags_full_path[file.path] = size_etag

                if generate_file_name_only:
                    file_sizes_etags_only_names[file_name_without_path] = size_etag

            line_number += 1

        FilesStructures = collections.namedtuple("FilesStructures", ["all_files_full_path",
                                                                     "file_sizes_etags_full_path",
                                                                     "all_files_only_names",
                                                                     "file_sizes_etags_only_names"])

        return FilesStructures(all_files_full_path, file_sizes_etags_full_path,
                               all_files_only_names, file_sizes_etags_only_names)


def etag_is_hash(etag):
    return "-" not in etag


def file_exists_name_size(file_name, size, etag, file_dictionary):
    if file_name in file_dictionary and file_dictionary[file_name].size == size and \
            not (etag_is_hash(file_dictionary[file_name].etag) and etag_is_hash(etag)):
        return True

    return False


def check_files(source, source_prefix_filter_and_strip,
                destination, destination_prefix_filter_and_strip,
                output_file_path, ignore_paths):
    # Load source file
    origin_files = read_files_file(source, source_prefix_filter_and_strip, include_all=False, generate_file_name_only=ignore_paths)
    destination_files = read_files_file(destination, destination_prefix_filter_and_strip, include_all=True, generate_file_name_only=ignore_paths)

    print("Origin files     :", len(origin_files.all_files_full_path))
    print("Destination files:", len(destination_files.all_files_full_path))

    count = 0

    output_file = open(output_file_path, "w")

    missing_files_count = 0

    for origin_file in origin_files.all_files_full_path:
        count += 1
        if count % 10000 == 0:
            print("Done {} of {}".format(count, len(origin_files.all_files_full_path)))

        file_in_destination = origin_file in destination_files.all_files_full_path

        if file_in_destination:
            continue

        if ignore_file(origin_file.path, origin_file.size):
            continue

        file_name_exists = file_exists_name_size(origin_file.path, origin_file.size,
                                                 origin_file.etag, destination_files.file_sizes_etags_full_path)

        if file_name_exists:
            continue

        if ignore_paths:
            origin_file_without_path = remove_path(origin_file)

            file_in_destination = origin_file_without_path in destination_files.all_files_only_names

            if file_in_destination:
                continue

            file_name_exists = file_exists_name_size(origin_file_without_path.path, origin_file_without_path.size,
                                                     origin_file_without_path.etag, destination_files.file_sizes_etags_only_names)

            if file_name_exists:
                continue

        output_file.write("{}\t{}\t{}\n".format(origin_file.path, origin_file.size, origin_file.etag))
        missing_files_count += 1

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

    parser.add_argument("--ignore-paths", action="store_true", help="Will ignore paths. Will assume that a file exists if the name+size or name+size+md5 (if possible) is the same even if in a different directory")

    args = parser.parse_args()

    check_files(args.source, args.source_prefix_filter_and_strip,
                args.destination, args.destination_prefix_filter_and_strip,
                args.output, args.ignore_paths)


if __name__ == "__main__":
    main()
