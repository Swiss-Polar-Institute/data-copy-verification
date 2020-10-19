#!/usr/bin/env python3

import argparse
import configparser
import io
import os
import sys
import textwrap

import boto3


# To enable boto logging
# boto3.set_stream_logger('')


def print_configuration_file_example():
    sys.stderr.write(textwrap.dedent("""\
                It needs to be a json file with this format:

                [authentication]
                aws-access-key-id = access-key
                aws-secret-access-key = secret-key
                # Optional: endpoint-url = https://s3.epfl.ch
                """))


def default_configuration_file():
    return os.path.join(os.getenv("HOME"), ".list-s3")


def read_configuration(section, key, configuration_path=None):
    if configuration_path is None:
        configuration_path = default_configuration_file()

    if not os.path.isfile(configuration_path):
        sys.stderr.write("File {} doesn't exist".format(configuration_path))
        print_configuration_file_example()
        sys.exit(1)

    config = configparser.ConfigParser(defaults={"endpoint-url": None})

    config.read(configuration_path)

    if section not in config or key not in config[section]:
        raise LookupError("Cannot read {}/{} from {}".format(section, key, configuration_path))

    return config[section][key]


def create_list_of_files(bucket, output_file_name, configuration_file):
    if os.path.isfile(output_file_name):
        sys.stderr.write("File {} already exists, aborting".format(output_file_name))
        sys.exit(1)

    aws_access_key_id = read_configuration("authentication", "aws-access-key-id", configuration_file)
    aws_secret_access_key = read_configuration("authentication", "aws-secret-access-key", configuration_file)
    aws_endpoint_url = read_configuration("authentication", "endpoint-url", configuration_file)

    s3 = boto3.resource(service_name="s3",
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        endpoint_url=aws_endpoint_url)

    bucket = s3.Bucket(bucket)

    files = bucket.objects.filter(Prefix="").all()

    output_file = io.open(output_file_name, "w", encoding="utf-8")

    count = 0

    for file in files:
        count += 1
        output_file.write(file.key + "\t" + str(file.size) + "\t" + file.e_tag.replace('"', '') + "\n")

        if count % 10000 == 0:
            print("{} {}".format(count, file.key))

    output_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lists all the files in the BUCKET and saves it with its ETag (usually an MD5 checksum) into DESTINATION_FILE")
    parser.add_argument("bucket", help="Bucket of where the files should be listed")
    parser.add_argument("destination_file", help="Destination file: where to save the list of files")
    parser.add_argument("--configuration", help=f"Configuration file. Defaults to {default_configuration_file()}")

    args = parser.parse_args()

    create_list_of_files(args.bucket, args.destination_file, args.configuration)
