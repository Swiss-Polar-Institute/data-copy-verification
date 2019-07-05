#!/usr/bin/env python3

import argparse
import subprocess
import datetime
import os
import sys
import time

# This was used only once to upload a series of files. It has not been tested more than that case.
# In normal circumstances better avoid using it and upload the files using another software, use
# the rest of utilities to *verify* the data instead of this one to upload it.


def write_to_log(cmd, exit_code):
    f = open("aws-upload.txt", "a")
    f.write("log\t" + str(datetime.datetime.now()) + "\t" + " ".join(cmd) + "\t" + str(exit_code) + "\n")
    f.close()


def upload_files(missing_files_file, local_base_directory, remote_base_directory, s3_bucket):
    f = open(missing_files_file, "r")

    lines = f.readlines()

    total_number_lines = len(lines)

    start_time = time.time()

    count = 0
    for line in lines:
        count += 1
        line = line.rstrip()
        file_name = line.split("\t")[0]

        if file_name.startswith("./"):
            file_name = file_name[2:]

        local_file_name = os.path.join(local_base_directory, file_name)

        print("Is going to upload file {} of {} - elapsed time: {} minutes".format(count, total_number_lines, (time.time() - start_time) / 60))

        if os.path.isdir(local_file_name):
            print("Skips because it is a directory")
            write_to_log("No command for {} is a directory".format(file_name), "0")
            continue

        remote_file_name = os.path.join(remote_base_directory, file_name)
        cmd = ["aws", "s3", "cp", "--endpoint-url=https://s3.epfl.ch", local_file_name, "s3://{}/{}".format(s3_bucket, remote_file_name)]

        exit_code = subprocess.call(cmd)

        write_to_log(cmd, exit_code)

        if exit_code != 0:
            print("Error, exit code:", exit_code)
            sys.exit(1)

    print("Total time: {} minutes".format((time.time() - start_time) / 60))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("missing_files_file", help="Missing files list (one file per line, can have tabs only first column is used)")
    parser.add_argument("local_base_directory", help="Local base directory - it's prepended on each line of the missing_files_file line, can be empty")
    parser.add_argument("remote_base_directory", help="Remote (S3) base directory where to upload the files")
    parser.add_argument("s3_bucket", help="s3_bucket to upload")

    args = parser.parse_args()

    upload_files(args.missing_files_file, args.local_base_directory, args.remote_base_directory, args.s3_bucket)


if __name__ == "__main__":
    main()
