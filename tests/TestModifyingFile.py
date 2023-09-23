import unittest
import os
import tempfile
import shutil

def modify_file(base_directory, relative_path, content_to_append):
    # Resolve the full path relative to the base directory
    full_path = os.path.join(base_directory, relative_path)

    if not os.path.exists(full_path):
        print(f"File {full_path} does not exist!")
        return

    with open(full_path, 'a+') as f:
        f.write(content_to_append)
        
    print(f"Successfully modified {full_path}")
    

class TestModifyFile(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_file = "sample.txt"
        self.sample_file_path = os.path.join(self.test_dir, self.sample_file)
        with open(self.sample_file_path, 'w') as f:
            f.write("Initial content.")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_modify_file(self):
        append_content = "\nAppended content."
        modify_file(self.test_dir, self.sample_file, append_content)

        with open(self.sample_file_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, "Initial content." + append_content)

if __name__ == "__main__":
    unittest.main()
