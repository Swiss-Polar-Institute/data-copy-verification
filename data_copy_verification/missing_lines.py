#!/usr/bin/env python3

import argparse


def read(file_path):
    lines = set()
    for line in open(file_path):
        line = line.rstrip()
        lines.add(line)

    return lines


def print_lines(lines):
    lines_list = list(lines)
    lines_list.sort()

    for line in lines_list:
        print(line)


def main(origin_path, destination_path):
    origin_set = read(origin_path)
    destination_set = read(destination_path)

    missing_lines_destination = origin_set - destination_set
    extra_lines_destination = destination_set - origin_set

    print(f'* Missing lines in {destination_path}:')
    print_lines(missing_lines_destination)

    print()
    print(f'* Extra lines in {destination_path}:')
    print_lines(extra_lines_destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to list lines that are missing/extra between two files removing duplicates and sorting them')
    parser.add_argument('origin')
    parser.add_argument('destination')

    args = parser.parse_args()
    main(args.origin, args.destination)