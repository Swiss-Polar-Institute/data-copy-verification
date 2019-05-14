#!/usr/bin/env python

import hashlib
import os
import datetime


def size_of_file(full_path_file):
    return int(os.path.getsize(full_path_file))


def hash_of_file(full_path_file):
    blocksize = 128 * 1024 * 1024   # 128 MB

    md5 = hashlib.md5()

    with open(full_path_file, "rb") as file_calculating_hash:
        file_buffer = file_calculating_hash.read(blocksize)
        while len(file_buffer) > 0:
            md5.update(file_buffer)
            file_buffer = file_calculating_hash.read(blocksize)

    return md5.hexdigest()


def calculate_hashes(prefix, directory, output_file):
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
            output.write(relative_dir + "\td41d8cd98f00b204e9800998ecf8427e\t0\n")

        for file in files:
            full_path_file = os.path.join(root, file)
            relative_file = full_path_file[len(directory):]
            output.write(prefix + relative_file + "\t" + hash_of_file(full_path_file) + "\t" + str(size_of_file(full_path_file)) + "\n")

        if count == 10000:
            print("Processing " + directory + "Number of files done: " + str(count))

    output.close()


def main():
    # seagate
    # shareds = ["ace_data", "data_admin", "data_staging", "ethz_forecast_data", "external_data", "intranet_documents",
    #            "media ropos", "ship_data", "work_leg1", "work_leg2", "work_leg3", "work_leg4"]

    # western
    shareds = ["ship_data_end_of_leg4", "media_end_of_leg3", "ace_data_end_of_leg4"]


    for shared in shareds:
        directory = os.path.join("/volume1", shared)
        output_file = os.path.join("/volume1/data_admin/verification2/" + shared + ".txt")
        prefix = shared + "/"

        calculate_hashes(prefix, directory, output_file)

if __name__ == "__main__":
    main()