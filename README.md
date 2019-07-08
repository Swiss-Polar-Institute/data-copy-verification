# data-copy-verificatoin

This is a set of utilities to verify that files have been copied from:

* local mounted storage (e.g. NAS) to object storage (such as S3 or minio)
* from object storage to object storage
* from mounted storage to mounted storage

It supports:
* directory renaming (where the directories can have been renamed on the copy)
* check a subset of directories
* uses Amazon ETag which usually uses MD5 checksums and file hashes, but also handles verifications by name+size only
* supports (optionally) files that have been moved between directories

Note that any reference to S3 is made to refer to object storage in general. This could be Amazon S3, or minio, for example.

## Motivation
The motivation for the creation of these tools was to verify that millions of files, containing terabytes of data, were uploaded correctly from a NAS to object storage.

## Installation
```
git clone https://github.com/Swiss-Polar-Institute/data-copy-verification.git
cd data-copy-verification
virtualenv -p python3
. venv/bin/activate
pip3 install -r requirements.txt
```

## Usage for files copied to object storage
* Copy the data (e.g. from `/mnt/data` to `e09e32e2b8944f189aeda41d9a301d3d` using a tool such as CloudBerry, AWS Command Line Interface, etc.)
* Create the file `$HOME/.list-s3` and add the following text:
```
[authentication]
aws-access-key-id = TheAccessKey
aws-secret-access-key = TheSecretAccessKey
endpoint-url = https://someEndPointIfNotDefaultAWS
```

Execute:
```
cd data_copy_verification/
./list_local_files.py /mnt/data localfiles-list.txt # localfiles-list.txt will contain a list of all files in /mnt/data
./list_s3_files.py e09e32e2b8944f189aeda41d9a301d3d bucket-list.txt # bucket-list.txt will contain a list of all files in object storage bucket
./verify_no_missing_files.py localfiles-list.txt bucket-list.txt missing-files.txt # missing-files.txt will contain a list of all files that are in /mnt/data but not in the object storage bucket
```
The output will be a file (`missing-files.txt`) with the list of missing files, their sizes and hash/ETags.

Note that `verify_no_missing_files.py` considers files to be equal only if:

* `file_path+file_name`, `size` and `ETags` are the same
* unless one of the ETags contains "-" at the end: then the ETag comparison will be ignored and the comparison based on the file_path+file_name and size only (see Background Notes section below for more information about the reasons for this). 

Explore the utilities for different options (e.g. `verify_no_missing_files.py -h`).

The `verify_no_missing_files.py` has a few options:
* One is to filter a subset of the origin or destination file (only lines starting with the options passed to `--source-prefix-filter-and-strip` or `--destination-prefix-filter-and-strip` are considered and the initial part of the file path is stripped).
* Another option is `--ignore-paths`: consider usage of this option if files have been moved to different directories in the destination storage. Not using this option may result in
 false positives in `missing-files.txt` if files have changed directory. This option will consider the file to exist if the filename+size+hash exists in the destination file, regardless of the file path. Note that if the file in the origin/destination has an ETag like `b8807f12b9db982da89f6411f408f4d7-2` (see Background Notes section below) it will ignore the hash comparison and consider the files the same based on filename (without the path) and size only.

Memory performance of `--ignore-paths` option:
If the option `--ignore-paths` is used, this will increase the memory consumption. For around 4 million files, about 5 GB of RAM is used. Without the `--ignore-paths` option, the memory usage is about half that, however it would reduce the number of false positives in `missing-files.txt`. 

If the number of missing files in `missing-files.txt` without the `--ignore-paths` option is low compared with the total number of files being copied, it is simpler and more memory efficient, to use other means to check if these files exist or not in the destination location. For example, use `grep` or a find function in the bucket-list.txt file to verify manually if they are present. This would need to be done manually or implemented separately by the user (it does not yet exist in this set of tools). 

If the number of missing files in missing-files.txt is high, then another solution would also need to be implemented.

## Unit tests
To execute all unit tests:

```
python3 -m unittest discover
```

Or only one unit test class:
```
python3 -m unittest tests/test_verify_no_missing_files.py
```
## Background notes

### File hashes and ETags

These tools use hashes, or in the case of object storage-based files, ETags, to compare the files before and after copy to ensure they have not been modified during this process. Within these tools, where hashes are used (i.e for files not on object storage), these are MD5 checksums. ETags are usually MD5 checksums as well, so they can be compared. If a file has been copied without changes or corruption, then the original and copied files will have identical hashes or ETags. However when considering files moved to object storage, there are some circumstances in which this may not be the case. Aside from when the file has been changed or corrupted, these circumstances are described here: 

1. *A "-" occurs towards the end of the ETag in the copied file, if this hash is not an MD5 checksum.* When using tools to upload files to object storage, it is possible to choose when to split a file. There is always a limit to this, but it can be set smaller or larger depending on your preferences. If the file is smaller than this limit, then it will be uploaded to the object storage bucket in one go and therefore the ETag will be the MD5 checksum (with no "-"). However if the file is larger than this limit, then it will be uploaded in parts and the ETag will no longer be the MD5 checksum. Therefore the ETag of the uploaded file will no longer be comparable with that of the original file.

1. *Files that have SSE-C or SSE-KMS encryption.* Another occasion on which a file uploaded to object storage has an ETag that will not be an MD5 checksum is if the file has SSE-C or SSE-KMS encryption.

When using these tools, the main issue that could cause problems here is the copying of large files and the resulting ETag fitting the circumstances of point one above. This problem is overcome within the tools by comparing the files by path+size, where the ETag contains a "-".
