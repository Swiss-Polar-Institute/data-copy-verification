#!/usr/bin/env python3

import argparse


def read(file_path):
    lines = set()
    for line in open(file_path):
        line = line.rstrip()
        if line in lines:
            print(f'Duplicated line in {file_path}:')
            print(line)
        lines.add(line)

    return lines


def format_lines_to_print(lines):
    lines_list = []

    for line in lines:
        hash = line[0:32]
        file_name = line[34:]

        lines_list.append((hash, file_name,))

    lines_list.sort(key=lambda i: i[1])

    return lines_list


def print_lines(lines):
    lines_list = format_lines_to_print(lines)

    for line in lines_list:
        print(f'{line[0]}  {line[1]}')


def diff_lines(bucket_list_path, model_list_path):
    bucket_set = read(bucket_list_path)
    model_set = read(model_list_path)

    missing_files_in_bucket = model_set - bucket_set
    extra_files_in_bucket = bucket_set - model_set

    return {'missing_files_in_bucket': missing_files_in_bucket,
            'extra_files_in_bucket': extra_files_in_bucket,
            'files_in_bucket': len(bucket_set),
            'files_in_destination': len(model_set),
            }


def main(bucket_path, model_path):
    result = diff_lines(bucket_path, model_path)

    missing_files_in_bucket = result['missing_files_in_bucket']
    extra_files_in_bucket = result['extra_files_in_bucket']

    print(f'* Number of files in bucket ({bucket_path}): {result["files_in_bucket"]}')
    print(f'* Number of files in model  ({model_path}): {result["files_in_destination"]}')

    print(f'* Missing files in {bucket_path}:')
    print_lines(missing_files_in_bucket)
    print(f'Total: {len(missing_files_in_bucket)}')

    print()
    print(f'* Extra files in {bucket_path}:')
    print_lines(extra_files_in_bucket)
    print(f'Total: {len(extra_files_in_bucket)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to list lines that are missing/extra between two files removing duplicates and sorting them')
    parser.add_argument('bucket')
    parser.add_argument('model')

    args = parser.parse_args()
    main(args.bucket, args.model)
