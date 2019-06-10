#!/usr/bin/env python3

import hashlib
import os
import datetime
import argparse
import time


def size_of_file(full_path_file):
    return int(os.path.getsize(full_path_file))


def hash_of_file(full_path_file):
    block_size = 512 * 1024 * 1024   # 512 MB

    md5 = hashlib.md5()

    with open(full_path_file, "rb") as file_calculating_hash:
        file_buffer = file_calculating_hash.read(block_size)
        while len(file_buffer) > 0:
            md5.update(file_buffer)
            file_buffer = file_calculating_hash.read(block_size)

    return md5.hexdigest()


def calculate_hashes(directory, output_file):
    output = open(output_file, "a")

    if not directory.endswith("/"):
        directory += "/"

    count = 0

    print("Starting: " + directory + " at " + str(datetime.datetime.now()))

    for root, dirs, files in os.walk(directory):
        count += 1

        for dir in dirs:
            full_path_dir = os.path.join(root, dir)
            relative_dir = full_path_dir[len(directory):]
            output.write(relative_dir + "\t0\td41d8cd98f00b204e9800998ecf8427e\n")

        for file in files:
            full_path_file = os.path.join(root, file)
            relative_file = full_path_file[len(directory):]
            output.write(relative_file + "\t" + str(size_of_file(full_path_file)) + "\t" + hash_of_file(full_path_file) + "\n")

        if count == 10000:
            print("Processing " + directory + "Number of files done: " + str(count))

    output.close()


def main():
    parser = argparse.ArgumentParser()
    parser.description("From a local system it generates a file with list of files, sizes and md5. md5 because this is what Amazon S3 uses as ETag (unless the file was uploaded in chunks)")
    parser.add_argument("base_directory", help="root directory of the list of files")
    parser.add_argument("output_file", help="Output file: each line contains the name of the file, file size (bytes) and md5 hash")

    args = parser.parse_args()

    start_time = time.time()
    calculate_hashes(args.base_directory, args.output_file)

    end_time = time.time()
    print("Total time in hours {0:.2f}: ", (end_time - start_time) / 3600)
    print("Output file:" , args.output_file)


if __name__ == "__main__":
    main()
