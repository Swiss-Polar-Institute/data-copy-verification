#!/usr/bin/env python3

import boto3
import json
import os
import io

# boto3.set_stream_logger('')

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
    # bucket = s3.Bucket("113269-9ccd1ea1e54d9e8cad0e2a15cbf98fa6")  # NAS Seagate bucket
    bucket = s3.Bucket("113269-f7f4a7c9863473f08cb883a2b00c95cf")   # NAS Western bucket

    counting = 0

    prefixes = ["intranet_documents",
     "intranet_documents_end_of_leg2",
     "ace_data",
     "ace_data_end_of_leg2",
     "ace_data_end_of_leg3",
     "ace_data_old",
     "ace_data_old2",
     "data_admin",
     "data_admin_end_of_leg2",
     "data_admin_end_of_leg3",
     "data_admin_end_of_leg4",
     "data_staging",
     "data_staging_end_of_leg2",
     "data_staging_end_of_leg3",
     "data_staging_end_of_leg4",
     "data_staging_old2",
     "ethz_forecast_data_end_of_leg4",
     "ethz_forecast_data_old2",
     "external_data",
     "external_data_end_of_leg2",
     "external_data_end_of_leg3",
     "external_data_end_of_leg4",
     "external_data_old2",
     "intranet_documents_end_of_leg3",
     "intranet_documents_end_of_leg4",
     "intranet_documents_old2",
     "media_old2",
     "NetBackup",
     "ropos_20170217",
     "scripts",
     "ship_data",
     "ship_data_end_of_leg2",
     "ship_data_end_of_leg3",
     "ship_data_old2",
     "work_leg1",
     "work_leg1_end_of_leg2",
     "work_leg1_end_of_leg4",
     "work_leg1_old2",
     "work_leg2",
     "work_leg2_end_of_leg2",
     "work_leg2_end_of_leg4",
     "work_leg2_old2",
     "work_leg3",
     "work_leg3_end_of_leg2",
     "work_leg3_end_of_leg3",
     "work_leg3_end_of_leg4",
     "work_leg3_old2",
     "work_leg4_end_of_leg4"]

    count = 0
    for prefix in prefixes:
        files = bucket.objects.filter(Prefix=prefix + "/").all()

        output_file_name = "list-s3-files-western-{}".format(prefix)
        output_file = io.open(output_file_name + ".txt", "w", encoding="utf-8")

        inner_count = 0
        for file in files:
            # print("inner_count:", inner_count)
            counting += 1
            output_file.write(file.key + "\t" + str(file.size) + "\t" + file.e_tag.replace('"', '') + "\n")

            if counting % 1000 == 0:
                write_state(file.key)
                print(str(counting) + " " + file.key)

            inner_count += 1

        output_file.close()
        os.system("gzip {}.txt".format(output_file_name))
        os.system("scp {}.txt.gz admin@wiki.glaceexpedition.ch:backups/s3".format(output_file_name))
        os.system("rm {}.txt.gz".format(output_file_name))

        count += 1
        print("finished {} {}/{}".format(prefix, count, len(prefixes)))

    print("all finished!")


if __name__ == "__main__":
    main()
