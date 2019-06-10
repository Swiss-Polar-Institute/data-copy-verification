#!/usr/bin/env python3

import argparse
import subprocess
import datetime
import os


def write_to_log(cmd, exit_code):
    f = open("aws-upload.txt", "a")
    f.write("log\t" + str(datetime.datetime.now()) + "\t" + " ".join(cmd) + "\t" + str(exit_code) + "\n")
    f.close()


def upload_files(missing_files_file, s3_bucket):
    f = open(missing_files_file, "r")

    lines = f.readlines()

    total_number_lines = len(lines)

    count = 0
    for line in lines:
        count += 1
        line = line.rstrip()
        (file_name, size, hash) = line.split("\t")

        local_file_name = "/volume1/{}".format(file_name)

        print("Is going to upload file {} of {}".format(count, total_number_lines))

        if os.path.isdir(local_file_name):
            print("Skips because it is a directory")
            write_to_log("No command for {} is a directory".format(file_name), "0")
            continue

        cmd = ["aws", "s3", "cp", "--endpoint-url=https://s3.epfl.ch", local_file_name, "s3://{}/{}".format(s3_bucket, file_name)]
        print(cmd)
        exit_code = subprocess.call(cmd)
        write_to_log(cmd, exit_code)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("missing_files_file", help="Missing files (3 columns with tabs, first column is the file name)")
    parser.add_argument("s3_bucket", help="s3_bucket to upload")

    args = parser.parse_args()

    upload_files(args.missing_files_file, args.s3_bucket)


if __name__ == "__main__":
    main()
