import unittest
import requests
from baekjoon_tui import *

class ParserTestCase(unittest.TestCase):
    category_parser: ProblemCategoryParser
    plist_parser: ProblemListParser

    def setUp(self):
        category_req = requests.get("https://acmicpc.net/step")
        self.category_parser = ProblemCategoryParser()
        self.category_parser.feed(category_req.text)

        plist_req = requests.get("https://acmicpc.net/step/1")
        self.plist_parser = ProblemListParser()
        self.plist_parser.feed(plist_req.text)

    def test_should_get_one_problem_category(self):
        # Extracting very first category
        first = self.category_parser.get_Nth_problem_category(0)

        # Note that these vaules are subject to change(unlikely, but it can be), so check these often.
        self.assertEqual(first.id, 1)
        self.assertEqual(first.title, "입출력과 사칙연산")
        self.assertEqual(first.total_count, 15)

    def test_should_get_all_problem_categories(self):
        all_category = self.category_parser.get_all_problem_category()
        for category in all_category:
            self.assertGreater(category.id, -1)
            self.assertNotEqual(category.title, '')
            self.assertNotEqual(category.description, '')
            self.assertGreaterEqual(category.total_count, -1)

    def test_should_get_one_problem_list(self):
        # Extracting very first problem list as did
        first = self.plist_parser.get_Nth_problem_preview(0)

        self.assertEqual(first.id, 2557)
        self.assertEqual(first.title, "Hello World")
        self.assertGreater(first.accepted_submits, 0)
        self.assertGreater(first.submits, 0)

    def test_should_get_all_problem_list(self):
        all_problems = self.plist_parser.get_all_problem_previews()
        for preview in all_problems:
            self.assertGreater(preview.id, 999)
            self.assertNotEqual(preview.title, '')
            self.assertGreater(preview.accepted_submits, -1)
            self.assertGreater(preview.submits, -1)

if __name__ == "__main__":
    unittest.main()