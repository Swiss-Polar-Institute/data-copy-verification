from data_copy_verification import verify_no_missing_files
import unittest
import tempfile


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
        set_of_files = verify_no_missing_files.file_to_list(fd_temp.name)

        self.assertEqual(set_of_files[0], {"ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291",
                                           "ace_data/a_file/big_file\t3006477107\te7a30baab848c6560ef87aac602583-1"})
        self.assertEqual(set_of_files[1], {"ace_data/a_file/big_file": 3006477107})

    def test_check_by_name(self):
        fd_temp = self._generate_file()

        files = verify_no_missing_files.file_to_list(fd_temp.name)

        self.assertFalse(verify_no_missing_files.file_exists_name_size("does_not_exist", 1000, files[1]))
        self.assertFalse(verify_no_missing_files.file_exists_name_size("ace_data/a_file/big_file", 2222, files[1]))
        self.assertTrue(verify_no_missing_files.file_exists_name_size("ace_data/a_file/big_file", 3006477107, files[1]))

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

        verify_no_missing_files.check_files(origin_temp.name, destination_temp.name, output_file.name)
        self.assertEqual(self._read_file_to_list(output_file.name), [])

    def test_check_missing_files(self):
        origin_temp = tempfile.NamedTemporaryFile(mode="w")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        origin_temp.write("ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        origin_temp.write("big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d\n")

        destination_temp = tempfile.NamedTemporaryFile(mode="w")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        destination_temp.write("ace_data/ACS/ace_2017-02-19+15-53.bin\t18193\td845983211e31b1a140df007996a9f06\n")
        destination_temp.write("big_file\t99999\teb6514d19f336aaafa526921423d5d04\n")

        origin_temp.seek(0)
        destination_temp.seek(0)

        output_file = tempfile.NamedTemporaryFile()

        verify_no_missing_files.check_files(origin_temp.name, destination_temp.name, output_file.name)
        self.assertEqual(self._read_file_to_list(output_file.name), ['ace_data/ACS/ace_2017-02-19+15-5X.bin\t18193\td845983211e31b1a140df007996a9f06',
                                                                     'big_file\t2492941031\t2f85e4aafce87e47b34547fc078ced4d'])


if __name__ == '__main__':
    unittest.main()
