# data-copy-verificatoin

This is a set of utilities to verify that files have been copied from:

* local mounted storage (e.g. NAS) to S3
* from S3 to S3
* from mounted storage to mounted storage

It supports:
* directory renaming (the directories can have been renamed on the copy)
* check a subset of directories
* uses Amazon ETag usually md5, but also handles verifications by name+size only
* supports (optionally) files that have been moved

## Example
* Copy the data (e.g. from `/mnt/data` to `e09e32e2b8944f189aeda41d9a301d3d`)
* Create the file `$HOME/.list-s3` :
```
[authentication]
aws-access-key-id = TheAccessKey
aws-secret-access-key = TheSecretAccessKey
endpoint-url = https://someEndPointIfNotDefaultAWS
```

Execute:
```
./list_local_files.py /mnt/data localfiles-list.txt
./list_s3_files.py e09e32e2b8944f189aeda41d9a301d3d bucket-list.txt
./verify_no_missing_files.py localfiles-list.txt bucket-list.txt missing-files.txt
```
The output will be a file (`missing-files.txt`) with the list of missing files, their sizes and hash/ETags.

Explore the utilities for different options (e.g. `verify_no_missing_files.py -h`)

Note that `verify_no_missing_files.py` considers files to be equal only if:

* `file_path+file_name`, `size` and `etags` are the same
* unless one of the etags contains "-" at the end: then the etag comparison will be ignored and base it on the file_path+file_name, size only

ETags are used because in the majority of the files when we prepared these utilities the ETags were md5 and we wanted to detect changes of the files between the current local storage and the uploaded S3.

The `verify_no_missing_files.py` has a few options:
One is to filter a subset of the origin or destination file (only lines starting with the options passed to `--source-prefix-filter-and-strip` or `--destination-prefix-filter-and-strip` are considered and the initial part of the file path is stripped).

Another option is `--ignore-paths`: this will consider the file to exist if the filename+size+hash exist in the destination file regardless of the flie path. Note that if the file in the origin/destination has an etag like `b8807f12b9db982da89f6411f408f4d7-2` (uploaded in chunks) it will ignore the hash comparison and consider the files the same based on filename (without the path) and size.

Memory performance:
If using `--ignore-paths` for a 4 milion files about 5 GB of RAM is used. Without `--ignore-paths` the memory usage is about half.

In memory consumption is a problem and `--ignore-paths` needs to be used: if the number of missing files without the `--ignore-paths` is low compared with the number of total files a second pass verifying if the file exists ignoring the file path could be done. This would be more memory efficient than the current implementation.

# Unit tests
To execute all unit tests:

```
python3 -m unittest discover
```

Or only one unit test class:
```
python3 -m unittest tests/test_verify_no_missing_files.py
```
