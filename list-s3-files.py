#!/usr/bin/env python

import boto3
import json
import os
import io

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

    # bucket = s3.Bucket("13269-d41d8cd98f00b204e9800998ecf8427e")  # glace bucket
    #bucket = s3.Bucket("113269-9ccd1ea1e54d9e8cad0e2a15cbf98fa6")  # NAS Seagate bucket
    bucket = s3.Bucket("113269-f7f4a7c9863473f08cb883a2b00c95cf")   # NAS Western bucket

    counting = 0

    prefixes = ["ace_data_end_of_leg4/", "ship_data_end_of_leg4/", "media_end_of_leg3/"]

    for prefix in prefixes:
        files = bucket.objects.filter(Prefix=prefix).all()

        output_file = io.open("list-s3-files-western.txt", "w", encoding="utf-8")

        for file in files:
            counting += 1
            output_file.write(file.key + "\t" + str(file.size) + "\t" + file.e_tag.replace('"', '') + "\n")

            if counting % 1000 == 0:
                write_state(file.key)
                print(str(counting) + " " + file.key)

        output_file.close()

        print("finished prefix!")

    print("all finished!")


if __name__ == "__main__":
    main()
