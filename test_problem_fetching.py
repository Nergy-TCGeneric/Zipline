import unittest
import requests
from baekjoon_tui import ProblemCategoryParser, ProblemParser, ProblemCategory

class ParserTestCase(unittest.TestCase):
    category_parser: ProblemCategoryParser

    def setUp(self):
        req = requests.get("https://acmicpc.net/step")
        self.category_parser = ProblemCategoryParser()
        self.category_parser.feed(req.text)

    def test_should_extract_one_essential_datum_from_table(self):
        # Extracting very first category
        first = self.category_parser.get_Nth_problem_category(0)

        # Note that these vaules are subject to change(unlikely, but it can be), so check these often.
        self.assertEqual(first.id, 1)
        self.assertEqual(first.title, "입출력과 사칙연산")
        self.assertEqual(first.total_count, 15)

    def test_should_extract_all_essential_data_from_table(self):
        all_category = self.category_parser.get_all_problem_category()
        for category in all_category:
            self.assertGreater(category.id, -1)
            self.assertNotEqual(category.title, '')
            self.assertNotEqual(category.description, '')
            self.assertGreaterEqual(category.total_count, -1)

if __name__ == "__main__":
    unittest.main()