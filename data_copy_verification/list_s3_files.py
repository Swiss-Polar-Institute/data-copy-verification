#!/usr/bin/env python3

import boto3
import json
import os
import io
import argparse
import sys
import textwrap

# To enable boto logging
# boto3.set_stream_logger('')


def read_configuration(key):
    configuration_path = os.path.join(os.getenv("HOME"), ".list-s3.conf")

    if not os.path.isfile(configuration_path):
        sys.stderr.write("File {} doesn't exist".format(configuration_path))
        sys.stderr.write(textwrap.dedent("""\
            It needs to be a json file with this format:
            {
                "aws_access_key_id": "the_access_key",
                "aws_secret_access_key": "the_secret_access_key"
            }"""))

        sys.exit(1)

    try:
        fp = open(configuration_path, "r")
        data = json.load(fp)

    except json.JSONDecodeError:
        sys.stderr.write("Not a JSON valid file {}".format(configuration_path))
        sys.exit(1)

    if key not in data:
        sys.stderr.write("Missing key {} in {}".format(key, configuration_path))
        sys.exit(1)

    value = data[key]
    return value


def create_list_of_files(bucket, output_file_name):
    if os.path.isfile(output_file_name):
        sys.stderr.write("File {} already exists, aborting".format(output_file_name))
        sys.exit(1)

    aws_access_key_id = read_configuration("aws_access_key_id")
    aws_secret_access_key = read_configuration("aws_secret_access_key")

    s3 = boto3.resource(service_name="s3",
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key,
                     endpoint_url="https://s3.epfl.ch")

    bucket = s3.Bucket(bucket)

    count = 0
    files = bucket.objects.filter(Prefix="").all()

    output_file = io.open(output_file_name, "w", encoding="utf-8")

    inner_count = 0
    for file in files:
        count += 1
        output_file.write(file.key + "\t" + str(file.size) + "\t" + file.e_tag.replace('"', '') + "\n")

        if count % 1000 == 0:
            print("{} {}".format(count, file.key))

        inner_count += 1

    output_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List all the files in a bucket and saves it with its e_tag (usually md5) into destination_file")
    parser.add_argument("bucket", help="Bucket to list the files from")
    parser.add_argument("destination_file", help="Destination file where to save the list of files")

    args = parser.parse_args()

    create_list_of_files(args.bucket, args.destination_file)