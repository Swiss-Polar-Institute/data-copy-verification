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


def diff_lines(origin_path, destination_path):
    origin_set = read(origin_path)
    destination_set = read(destination_path)

    missing_lines_destination = origin_set - destination_set
    extra_lines_destination = destination_set - origin_set

    return {'missing_lines_destination': missing_lines_destination,
            'extra_lines_destination': extra_lines_destination
            }


def main(origin_path, destination_path):
    result = diff_lines(origin_path, destination_path)

    missing_lines_destination = result['missing_lines_destination']
    extra_lines_destination = result['extra_lines_destination']

    print(f'* Missing lines in {destination_path}:')
    print_lines(missing_lines_destination)
    print(f'Total: {len(missing_lines_destination)}')

    print()
    print(f'* Extra lines in {destination_path}:')
    print_lines(extra_lines_destination)
    print(f'Total: {len(extra_lines_destination)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to list lines that are missing/extra between two files removing duplicates and sorting them')
    parser.add_argument('origin')
    parser.add_argument('destination')

    args = parser.parse_args()
    main(args.origin, args.destination)
