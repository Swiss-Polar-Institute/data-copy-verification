#!/usr/bin/env python3

import argparse
import sys


def abort_if_line_incorrect(line, file_path, line_number):
    if line.count("\t") != 2:
        print("File path: {} Line Number: {} Not having 2 tabs".format(file_path, line_number), file=sys.stderr)
        print("Line: {}".format(line), file=sys.stderr)
        sys.exit(1)


def file_to_list(file_path, prefix_filter_and_ignore):
    if prefix_filter_and_ignore is None:
        prefix_filter_and_ignore = ""

    with open(file_path, mode="r", newline="\n") as f:
        files_invalid_hash = {}
        lines = set()

        line_number = 1

        for line in f.readlines():
            line = line.strip()

            abort_if_line_incorrect(line, file_path, line_number)

            if not line.startswith(prefix_filter_and_ignore):
                continue

            line = line[len(prefix_filter_and_ignore):]

            abort_if_line_incorrect(line, file_path, line_number)

            lines.add(line)

            if "-" in line[-5:]:
                (name, size, file_hash) = line.split("\t")
                files_invalid_hash[name] = int(size)

            line_number += 1

        return lines, files_invalid_hash


def file_exists_name_size(file_name, size, file_list):
    if file_name in file_list and file_list[file_name] == size:
        print("File existence based on name+size only: ", file_name)
        return True

    return False


def check_files(source, source_prefix_filter_and_strip, destination, destination_prefix_filter_and_strip, output_file_path):
    # Load source file
    (origin_files, origin_files_invalid_hash) = file_to_list(source, source_prefix_filter_and_strip)
    (destination_files, destination_files_invalid_hash) = file_to_list(destination, destination_prefix_filter_and_strip)

    print("Origin files     :", len(origin_files))
    print("Destination files:", len(destination_files))

    count = 0

    output_file = open(output_file_path, "w")

    missing_files_count = 0

    for origin_file in origin_files:
        file_in_destination = origin_file in destination_files

        if not file_in_destination:
            (name, size, file_hash) = origin_file.split("\t")
            size = int(size)
            base_file_name = name.split("/")[-1]
            if size != 0 and "@eaDir/" not in name and \
                    not base_file_name.startswith(".") and \
                    base_file_name != "Thumbs.db" and \
                    base_file_name != "desktop.ini" and \
                    not base_file_name.startswith("~") and \
                    not base_file_name.startswith("$"):

                file_name_exists = file_exists_name_size(name, size, destination_files_invalid_hash)
                if not file_name_exists:
                    output_file.write(origin_file + "\n")
                    missing_files_count += 1

        count += 1
        if count % 10000 == 0:
            print("Done {} of {}".format(count, len(origin_files)))

    output_file.close()

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
