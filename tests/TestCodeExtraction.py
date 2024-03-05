import unittest
import re


# def extract_code_from_text(text):
#     pattern = r"’’’python(.*?)’’’"
#     matches = re.findall(pattern, text, re.DOTALL)
#     code_only = '\n'.join(match.strip() for match in matches)  # Remove leading and trailing white spaces
#     return code_only

def extract_code_from_text_new(text, languages):
    code_blocks = {}
    
    for lang in languages:
        pattern = r"’’’" + re.escape(lang) + r"(.*?)’’’"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            code_only = '\n'.join(match.strip() for match in matches)
            code_blocks[lang] = code_only
    
    return code_blocks


class TestCodeExtraction(unittest.TestCase):

    def test_extract_code_from_text(self):
        languages = ["python", "js"]
        
        print(30*"-")
        # Test case 1: one block of code
        text1 = "This is some text. ’’’python\nprint('Hello, world!')\n’’’ This is some more text."
        extracted_code = extract_code_from_text(text1, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code.get("python"), "print('Hello, world!')")
        
        print(30*"-")
        # Test case 2: multiple blocks of code
        text2 = "Text here. ’’’python\nx = 5\n’’’ More text. ’’’python\ny = 10\n’’’"
        extracted_code = extract_code_from_text(text2, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code.get("python"), "x = 5\ny = 10")

        print(30*"-")
        # Test case 3: no blocks of code
        text3 = "This is a text with no code."
        extracted_code = extract_code_from_text(text3, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code, {})

        print(30*"-")
        # Test case 4: empty string
        text4 = ""
        extracted_code = extract_code_from_text(text4, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code, {})
        
        print(30*"-")
        # Test case 5: Blocks of code without programming language specified
        text5 = "This is some text. ’’’\nGeneric Code\n’’’ More text."
        extracted_code = extract_code_from_text(text5, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code, {})
        
        print(30*"-")
        # Test case 6: Blocks of code without programming language but with python and js
        text6 = "Text. ’’’python\nx = 5\n’’’ Text. ’’’\nGeneric Code\n’’’ ’’’js\nvar y = 10;\n’’’"
        extracted_code = extract_code_from_text(text6, languages)
        print(f"Extracted code: {extracted_code}")
        self.assertEqual(extracted_code.get("python"), "x = 5")
        self.assertEqual(extracted_code.get("js"), "var y = 10;")
        self.assertNotIn("", extracted_code)
        
        print(30*"-")

if __name__ == "__main__":
    unittest.main()