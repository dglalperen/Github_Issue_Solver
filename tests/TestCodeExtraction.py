import unittest
import re


def extract_code_from_text(text):
    pattern = r"’’’python(.*?)’’’"
    matches = re.findall(pattern, text, re.DOTALL)
    code_only = '\n'.join(match.strip() for match in matches)  # Remove leading and trailing white spaces
    return code_only


class TestCodeExtraction(unittest.TestCase):

    def test_extract_code_from_text(self):
        # Test case 1: one block of code
        text1 = "This is some text. ’’’python\nprint('Hello, world!')\n’’’ This is some more text."
        extracted_code = extract_code_from_text(text1)
        print(extracted_code)
        self.assertEqual(extracted_code, "print('Hello, world!')")
        

        # Test case 2: multiple blocks of code
        text2 = "Text here. ’’’python\nx = 5\n’’’ More text. ’’’python\ny = 10\n’’’"
        self.assertEqual(extract_code_from_text(text2), "x = 5\ny = 10")

        # Test case 3: no blocks of code
        text3 = "This is a text with no code."
        self.assertEqual(extract_code_from_text(text3), "")

        # Test case 4: empty string
        text4 = ""
        self.assertEqual(extract_code_from_text(text4), "")

if __name__ == "__main__":
    unittest.main()