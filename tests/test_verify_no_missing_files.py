from data_copy_verification import verify_no_missing_files
import unittest
import tempfile


class TestVerifyNoMissingFiles(unittest.TestCase):
    def test_file_to_list(self):
        fd_temp = tempfile.NamedTemporaryFile(mode="w")
        fd_temp.write("ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291\n")
        fd_temp.write("ace_data/a_file/big_file\t3006477107\te7a30baab848c6560ef87aac602583-1\n")
        fd_temp.seek(0)

        set_of_files = verify_no_missing_files.file_to_list(fd_temp.name)

        self.assertEqual(set_of_files[0], {"ace_data/ACS/ace_2017-02-19+15-52.bin\t171801\t9dbba3032755f200b3dc3ac79fdb9291",
                                           "ace_data/a_file/big_file\t3006477107\te7a30baab848c6560ef87aac602583-1"})
        self.assertEqual(set_of_files[1], {"ace_data/a_file/big_file": 3006477107})


if __name__ == '__main__':
    unittest.main()
