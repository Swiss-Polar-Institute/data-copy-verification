from data_copy_verification import verify_no_missing_files
import unittest
import tempfile
import collections


class TestVerifyNoMissingFiles(unittest.TestCase):
    @staticmethod
    def _generate_file():
        fd_temp = tempfile.NamedTemporaryFile(mode="w")
        fd_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        fd_temp.write("ace_data/a_file/big_file\t3006477107\te7a30baab848c6560ef87aac602583-1\n")
        fd_temp.seek(0)

        return fd_temp

    @staticmethod
    def _read_file_to_list(path):
        lines = []

        with open(path, "r") as fd:
            lines = [line.rstrip("\n") for line in fd]

        return lines

    def test_file_to_list(self):
        fd_temp = self._generate_file()
        set_of_files = verify_no_missing_files.read_files_file(fd_temp.name, None, include_all=False)

        self.assertEqual(set_of_files[0], {"ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291",
                                           "ace_data/a_file/big_file\t3006477107\te7a30baab848c6560ef87aac602583-1"})

        SizeEtag = collections.namedtuple("size_etag", ["size", "etag"])
        size_etag = SizeEtag(3006477107, "e7a30baab848c6560ef87aac602583-1")

        self.assertEqual(set_of_files[1], {"ace_data/a_file/big_file": size_etag})

    def test_check_by_name(self):
        fd_temp = self._generate_file()

        files = verify_no_missing_files.read_files_file(fd_temp.name, None, include_all=False)

        self.assertFalse(verify_no_missing_files.file_exists_name_size("does_not_exist", 1000, "94292929424aaa", files[1]))
        self.assertFalse(verify_no_missing_files.file_exists_name_size("ace_data/a_file/big_file", 2222, "94292929424aaa", files[1]))
        self.assertTrue(verify_no_missing_files.file_exists_name_size("ace_data/a_file/big_file", 3006477107, "94292929424aaa", files[1]))

    def test_check_files_no_missing_files(self):
        origin_temp = tempfile.NamedTemporaryFile(mode="w")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-53.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        origin_temp.write("big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-53.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        destination_temp.write("big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d\n")

        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, None, destination_temp.name, None, output_file.name)
        self.assertListEqual(self._read_file_to_list(output_file.name), [])

    def test_check_missing_files(self):
        origin_temp = tempfile.NamedTemporaryFile(mode="w")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        origin_temp.write("big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d\n")

        # Files that will be ignored
        origin_temp.write(".missing_file\t294242\t63dac3ef64e8edcb05321702731c3d83\n")
        origin_temp.write("/this/is/not/copied/@eaDir/\t294242\t63dac3ef64e8edcb05321702731c3d83\n")
        origin_temp.write("/some/directory/Thumbs.db\t294242\t63dac3ef64e8edcb05321702731c3d83\n")
        origin_temp.write("/here/it/comes/desktop.ini\t294242\t63dac3ef64e8edcb05321702731c3d83\n")
        origin_temp.write("/this/file/~notinthebackup\t294242\t63dac3ef64e8edcb05321702731c3d83\n")
        origin_temp.write("/this/file/$notinthebackup\t294242\t63dac3ef64e8edcb05321702731c3d83\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-53.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        destination_temp.write("big_file\t99999\teb6514d19f336aaafa526921423d5d04\n")

        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, None, destination_temp.name, None, output_file.name)
        self.assertListEqual(sorted(self._read_file_to_list(output_file.name)),
                             sorted(['ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06',
                                     'big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d']))

    def test_match_based_on_file_name_size(self):
        """Checks full hash from origin with non-hashed destination"""
        origin_temp = tempfile.NamedTemporaryFile(mode="w")

        # File exist - same file name + size
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")

        # File doesn't exist: no same file size
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        origin_temp.write("ace_data/missing_file\t7777\tae1a6f539c77b13aba2589ba8f22941b\n")

        # No missing file - it exist in the destination with a different etag (same name+size)
        origin_temp.write("no_missing_file\t8888\t3bf007aab4aab0b8e44b44112b2d76-2\n")

        # Missing file (no file with the same name size...)
        origin_temp.write("missing_file\t8888\t3bf007aab4aab0b8e44b44112b2d76-2\n")

        # Missing file (same name but not same size)
        origin_temp.write("missing_file_2\t8888\t3d4946a7d2719d01507fa661b69ea355-2\n")

        # Missing file: name matches but not size
        origin_temp.write("big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4-1\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb92-1\n")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-5X.bin\t9999\td845983211e31b1a140df007996a9f-2\n")
        destination_temp.write("big_file\t2492941031\t718c83aa3037894b869a9ab4c589f181-2\n")
        destination_temp.write("no_missing_file\t8888\t3bf007aab4aab0b8e44b44112b2d76-6\n")
        destination_temp.write("missing_file_2\t7777\t8a08e4adddce4b7c4df00d05959e368a-3\n")


        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, None, destination_temp.name, None, output_file.name)

        self.assertListEqual(sorted(self._read_file_to_list(output_file.name)),
                             sorted(['ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06',
                                     'ace_data/missing_file\t7777\tae1a6f539c77b13aba2589ba8f22941b',
                                     'missing_file_2\t8888\t3d4946a7d2719d01507fa661b69ea355-2',
                                     'missing_file\t8888\t3bf007aab4aab0b8e44b44112b2d76-2']))

    def test_match_prefix_ignore(self):
        origin_temp = tempfile.NamedTemporaryFile(mode="w")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        origin_temp.write("ace_data/ACS/test\t242131\t9cbce1ae85a074caa40df29afd9fb590\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("ace_data_end_of_leg4/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")

        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, "ace_data/", destination_temp.name, "ace_data_end_of_leg4/", output_file.name)

        self.assertListEqual(sorted(self._read_file_to_list(output_file.name)),
                             sorted(['ACS/test\t242131\t9cbce1ae85a074caa40df29afd9fb590']))

    def test_file_not_missing_etag(self):
        origin_temp = tempfile.NamedTemporaryFile(mode="w")
        origin_temp.write("not_missing_file\t242424\t9dbba3032755f200b3dc3ac79fdb92-1\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("not_missing_file\t242424\ta5cb30d858ec1f0be3b1bc08ea85e640")

        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, None, destination_temp.name, None, output_file.name)

        self.assertEqual(self._read_file_to_list(output_file.name), [])



if __name__ == '__main__':
    unittest.main()
