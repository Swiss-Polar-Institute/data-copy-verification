#!/usr/bin/env python

import boto3
import json
import os
import io


def last_marker():
    try:
        state_file = open("state.json", "r")
    except IOError:
        return None

    data = json.load(state_file)
    return data["marker"]


def write_state(marker):
    with open("state.json", "w") as state_file:
        state = {"marker": marker}
        json.dump(state, state_file)

def read_configuration(key):
    state_file = open(os.path.join(os.getenv("HOME"), ".list-s3.conf"), "r")
    data = json.load(state_file)
    return data[key]

def main():
    aws_access_key_id = read_configuration("aws_access_key_id")
    aws_secret_access_key = read_configuration("aws_secret_access_key")

    s3 = boto3.resource(service_name="s3",
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key,
                     endpoint_url="https://s3.epfl.ch")

    # bucket = s3.Bucket("13269-d41d8cd98f00b204e9800998ecf8427e") # glace bucket
    bucket = s3.Bucket("113269-9ccd1ea1e54d9e8cad0e2a15cbf98fa6") # NAS Seagate bucket

    counting = 0

    marker = last_marker()

    if marker is None:
        files = bucket.objects.all()
    else:
        files = bucket.objects.filter(Marker=marker)

    output_file = io.open("list-s3-files.txt", "a", encoding="utf-8")

    for file in files:
        counting += 1
        output_file.write(file.key + "\t" + str(file.size) + "\t" + file.e_tag.replace('"', '') + "\n")

        if counting % 1000 == 0:
            write_state(file.key)
            print(str(counting) + " " + file.key)

    output_file.close()

    print("finished!")


if __name__ == "__main__":
    main()
