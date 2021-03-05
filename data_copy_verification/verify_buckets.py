#!/usr/bin/env python3

import argparse
import datetime
import json
import subprocess
import sys

import missing_lines


def now():
    return f'{datetime.datetime.now():%Y%m%d-%H%M}'


def slugify_file_name(file_name):
    return file_name.replace(':', '_').replace('/', '_')


def rclone_hashsum(config, remote, output_directory, rclone_download, log_file=None):
    remote_slug = slugify_file_name(remote)
    output_file = f'{output_directory}/{remote_slug}-list-{now()}.txt'

    to_exec = ['rclone',
               '--config', config,
               'hashsum', 'MD5',
               remote,
               f'--output-file={output_file}',
               '--transfers=8']

    if log_file:
        to_exec += ['-vv', f'--log-file={log_file}']

    if rclone_download:
        to_exec += ['--download']

    to_exec_str = ' '.join(to_exec)
    print('Will execute:', to_exec_str)

    process = subprocess.run(to_exec)

    if process.returncode != 0:
        print('ERROR', to_exec_str)

    return output_file


def write_result(output_directory, remote, missing_files_info):
    remote_slugified = slugify_file_name(remote)
    output_file_path = f'{output_directory}/{remote_slugified}-result-{now()}.txt'

    with open(output_file_path, 'w') as output_file:
        output_file.write(f'REMOTE: {remote}\n')
        output_file.write('Missing files in bucket:\n')
        output_file.writelines(missing_files_info['missing_files_in_bucket'])

        output_file.write('\n')
        output_file.write('Extra lines in bucket:\n')
        output_file.writelines(missing_files_info['extra_files_in_bucket'])


def main(config_path, output_directory, rclone_log_file):
    with open(config_path) as json_file:
        buckets_config = json.load(json_file)

        return_value = 0
        for bucket_config in buckets_config:
            print(f'* {bucket_config["config_section"]}')
            remote = f'{bucket_config["config_section"]}:{bucket_config["bucket_name"]}/{bucket_config["path"]}'
            remote = remote.rstrip('/')
            bucket_listing_file = rclone_hashsum(bucket_config['rclone_config_file'], remote, output_directory,
                                                 bucket_config['rclone_download'], rclone_log_file)

            print(f'Bucket file: {bucket_listing_file}')
            print(f'Model file : {bucket_config["model_listing_file"]}')

            missing_files = missing_lines.diff_lines(bucket_config['model_listing_file'], bucket_listing_file)

            print('Missing objects in bucket:', len(missing_files['missing_files_in_bucket']))

            extra_files_in_bucket = 0
            if bucket_config['ignore_extra_files_bucket'] is False:
                extra_files_in_bucket = len(missing_files['extra_files_in_bucket'])
                print('Extra files in bucket', extra_files_in_bucket)

            if missing_files['missing_files_in_bucket'] or extra_files_in_bucket:
                return_value = 1

            write_result(output_directory, remote, missing_files)

    sys.exit(return_value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File to verify contents of the bucket against a known model')
    parser.add_argument('config', help='JSON file with the specifications of what to verify', type=str)
    parser.add_argument('output_directory', help='Directory with the output files of the verification', type=str)
    parser.add_argument('--rclone-log-file', help='If specified rclone will be executed with -v --log-file=PARAM')

    args = parser.parse_args()

    main(args.config, args.output_directory, args.rclone_log_file)
