#!/usr/bin/env python3

import argparse


def file_to_list(file_path, volume):
    with open(file_path) as f:
        files_invalid_hash = {}
        lines = set()

        if volume == "":
            startswith = ""
        else:
            startswith = volume + "/"

        for line in f.readlines():
            # line = line.replace("ace_data_end_of_leg4/", "ace_data/")
            # line = line.replace("ship_data_end_of_leg4/", "ship_data/")
            # line = line.replace("media_end_of_leg3/", "media/")
            if line.startswith(startswith):
                line = line.strip()
                # line = line[line.find("/")+1:]
                lines.add(line)

                if "-" in line[-5:]:
                    (name, size, hash) = line.split("\t")
                    files_invalid_hash[name] = int(size)

        return lines, files_invalid_hash


def check_by_name(file_name, size, file_list):
    if file_name in file_list and file_list[file_name] == size:
        print("File existance based on name+size only: ", file_name)
        return True

    return False


def check_files(source, destination, volume, output_file_path):
    # Load source file
    (origin_files, _) = file_to_list(source, volume)
    (destination_files, destination_files_invalid_hash) = file_to_list(destination, volume)

    print("Origin files     :", len(origin_files))
    print("Destination files:", len(destination_files))

    count = 0

    output_file = open(output_file_path, "w")

    for origin_file in origin_files:
        file_in_destination = origin_file in destination_files

        if not file_in_destination:
            (name, size, hash) = origin_file.split("\t")
            size = int(size)
            base_file_name = name.split("/")[-1]
            if size != 0 and "@eaDir/" not in name and not base_file_name.startswith(".") and base_file_name != "Thumbs.db" and base_file_name != "desktop.ini" and not base_file_name.startswith("~") and not base_file_name.startswith("$"):
                file_name_exists = check_by_name(name, size, destination_files_invalid_hash)
                if not file_name_exists:
                    output_file.write(origin_file + "\n")


        count += 1
        if count % 10000 == 0:
            print("Done {} of {}".format(count, len(origin_files)))

    output_file.close()

    print("Finished, see output at: {}".format(output_file_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source files: will check that all these files are in file2")
    parser.add_argument("destination", help="Destination files: will check that contains all the source files")
    parser.add_argument("volume", help="Destination files: will check that contains all the source files")
    parser.add_argument("output", help="Output file with the results")

    args = parser.parse_args()

    check_files(args.source, args.destination, args.volume, args.output)


if __name__ == "__main__":
    main()