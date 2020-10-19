#!/usr/bin/env python3

file = '/home/carles/glace/verification/s3/list-s3-files-seagate.txt'

directories = {}
for line in open(file):
    line = line.rstrip()
    path = line.split('\t')[0]

    directory = '/'.join(path.split('/')[0:-1])

    if directory in directories:
        directories[directory] += 1
    else:
        directories[directory] = 1

###########################
top_counter = 0
for k in sorted(directories, key=directories.get, reverse=True):
    print(k, directories[k])

    top_counter += 1

    if top_counter == 1000:
        break