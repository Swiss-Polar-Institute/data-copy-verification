# data-copy-verification

This is a set of utilities to verify that files have been copied from/to any combinations of:

* local mounted storage (e.g. NAS)
* object storage (e.g. Amazon S3, minio, etc. anything that boto3 can connect to)

It supports:
* directory renaming (where the directories have been renamed)
* check a subset of directories
* uses Amazon ETag which usually is MD5 hash, but also handles verifications by name+size only
* supports (optionally, via command line parameter) files that have been moved between directories

Note that any reference to S3 is made to refer to object storage in general. This could be Amazon S3, or minio, for example or any object storage that Boto3 Python libraries can connect to.

## Motivation
The motivation for the creation of these tools was to verify that millions of files, containing terabytes of data, were uploaded correctly from a NAS to object storage. It can also be used to monitor changes of a local storage or an object storage (create the reference and then check in some time if anything has changed).

## Installation
```
git clone https://github.com/Swiss-Polar-Institute/data-copy-verification.git
cd data-copy-verification
virtualenv -p python3 venv
. venv/bin/activate
pip3 install -r requirements.txt
```

## General usage
* Copy the data from source to destination (using your favourite tools to copy data)
* Generate two lists of files:
  * Using `list_local_files.py` if the files are available as a file system (local, NFS, Samba, etc.)
  * Using `list_s3_files.py` if the files are stored in an object storage
* Use `verify_no_missing_files.py` to verify that the destination directory of the copy has no missing files / no changed files

### Usage for files copied to object storage
* Copy the data from source to destination (e.g. from `/mnt/data` to `e09e32e2b8944f189aeda41d9a301d3d` using a tool such as CloudBerry, AWS Command Line Interface, etc.)
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

## File comparison

`verify_no_missing_files.py` considers files to be equal only if:

* `file_path+file_name`, `size` and `ETags` are the same
* unless one of the ETags contains "-" at the end: then the ETag comparison will be ignored and the comparison based on the file_path+file_name and size only (see Background Notes section below for more information about the reasons for this). 

The path can be ignored (then it uses the `file_name` without the path to the `file_name`) using the option `--ignore-paths`.

## Script running options

Explore the utilities for different options (e.g. `verify_no_missing_files.py -h`).

The `verify_no_missing_files.py` has a few options:
* Filter a subset of the origin or destination files: only lines starting with the options passed to `--source-prefix-filter-and-strip` or `--destination-prefix-filter-and-strip` are considered and the initial part of the file path is stripped.
* `--ignore-paths`: consider usage of this option if files have been moved to different directories in the destination storage. Not using this option may result in false positives in `missing-files.txt` if files have moved to a new directory. This option will consider the file to exist if the filename+size+hash exists in the destination file, regardless of the file path. Note that if the file in the origin/destination has an ETag like `b8807f12b9db982da89f6411f408f4d7-2` (see Background Notes section below) it will ignore the hash comparison and consider the files the same based on filename (without the path) and size only.

### Memory performance of `--ignore-paths` option:
If the option `--ignore-paths` is used, this will increase the memory consumption. For around 4 million files, about 5 GB of RAM is used. Without the `--ignore-paths` option, the memory usage is about half that.

If the number of missing files in `missing-files.txt` without the `--ignore-paths` option is low compared with the total number of files being copied, it is simpler and more memory efficient, to use other means to check if these files exist or not in the destination location. For example, use `grep` or a find function in the bucket-list.txt file to verify manually if they are present. This would need to be done manually or implemented separately by the user (it does not yet exist in this set of tools). 

## Unit tests
To execute all unit tests:

```
python3 -m unittest
```

Or only one unit test class:
```
python3 -m unittest test/test_verify_no_missing_files.py
```
## Background notes

### File hashes and ETags

These tools use hashes, or in the case of object storage-based files, ETags, to compare the files before and after copy to ensure they have not been modified during this process. Within these tools, where hashes are used (i.e for files not on object storage), these are MD5 hash. ETags in Amazon S3 and other compatible services are usually MD5 hash as well, so they can be compared. If a file has been copied without changes or corruption, then the original and copied files will have identical hashes or ETags. There are some circumstances in which this may not be the case. Aside from when the file has been changed or corrupted, these circumstances are: 

1. *A "-" occurs towards the end of the ETag in the copied file (eg. `b8807f12b9db982da89f6411f408f4d7-2`), if this hash is not an MD5 hash.* For large files the tool uploading the file might use it into multiple chunks (size depending on the tool, configuration and server side configuration). If the file is uploading in multipel chunks the ETag will not be the MD5 and will contain "-" towards the end. Therefore the ETag of the uploaded file will no longer be comparable with that of the original file.

1. *Files that have SSE-C or SSE-KMS encryption.* ETags will not be an MD5 hash if the file has SSE-C or SSE-KMS encryption.

The `verify_no_missing_files.py` tries to be as strict as possible and considers files to be the same:
 * if both hashes are full MD5: filepath (unless `--ignore-paths` was used), size and hashes are the same or
 * if one of the files (origen or destination) has a `-` in the hash: filepath (unless `--ignore-paths` was used) and size

This has been enough for our use case. A future possibility would be to download the files with an ETag with - from the object storage and calculate the hash locally. This was not needed in our use case.
