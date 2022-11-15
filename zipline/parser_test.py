import unittest
import requests
import browser_cookie3
from html_extractors import *
from zipline_component import Webpage


class ParserTestCase(unittest.TestCase):
    def test_should_get_one_problem_category(self):
        category_parser: ProblemCategoryParser = self.create_feeded_parser_of(
            Webpage.PROBLEM_CATEGORY
        )

        # Extracting very first category
        first = category_parser.get_Nth_problem_category(0)

        # Note that these vaules are subject to change(unlikely, but it can be), so check these often.
        self.assertEqual(first.id, 1)
        self.assertEqual(first.title, "입출력과 사칙연산")
        self.assertEqual(first.total_count, 14)

    def test_should_get_all_problem_categories(self):
        category_parser: ProblemCategoryParser = self.create_feeded_parser_of(
            Webpage.PROBLEM_CATEGORY
        )
        all_category = category_parser.get_all_problem_category()

        for category in all_category:
            self.assertGreater(category.id, -1)
            self.assertNotEqual(category.title, "")
            self.assertNotEqual(category.description, "")
            self.assertGreaterEqual(category.total_count, -1)

    def test_should_get_one_problem_list(self):
        plist_parser: ProblemListParser = self.create_feeded_parser_of(
            Webpage.PROBLEM_LIST
        )
        # Extracting very first problem list as did
        first = plist_parser.get_Nth_problem_preview(0)

        self.assertEqual(first.id, 2557)
        self.assertEqual(first.title, "Hello World")
        self.assertGreater(first.accepted_submits, 0)
        self.assertGreater(first.submits, 0)

    def test_should_get_all_problem_list(self):
        plist_parser: ProblemListParser = self.create_feeded_parser_of(
            Webpage.PROBLEM_LIST
        )
        all_problems = plist_parser.get_all_problem_previews()
        for preview in all_problems:
            self.assertGreater(preview.id, 999)
            self.assertNotEqual(preview.title, "")
            self.assertGreater(preview.accepted_submits, -1)
            self.assertGreater(preview.submits, -1)

    def test_should_get_problem_details(self):
        problem_parser: ProblemParser = self.create_feeded_parser_of(Webpage.PROBLEM)
        # Nothing to mention any further, do same thing as did
        detail = problem_parser.get_problem_details()

        # Comparing with actual problem, description and id must be identical
        self.assertEqual(detail.preview.id, 2557)
        self.assertEqual(detail.preview.title, "Hello World")
        self.assertGreater(detail.preview.accepted_submits, -1)
        self.assertGreater(detail.preview.submits, -1)
        self.assertEqual(detail.time_limit, "1 초")
        self.assertEqual(detail.memory_limit, "128 MB")
        self.assertEqual(detail.description, "Hello World!를 출력하시오.")
        self.assertEqual(detail.input_desc, "없음")
        self.assertEqual(detail.output_desc, "Hello World!를 출력하시오.")

    def test_should_fetch_every_data_to_prepare_solution_submit(self):
        html_reponse = get_html_response_of(Webpage.SUBMIT)
        if extract_username(html_reponse.text) == None:
            self.skipTest("user is not logged in, unable to proceed")

        csrf_parser: CSRFTokenParser = self.create_feeded_parser_of(Webpage.SUBMIT)
        csrf = csrf_parser.get_csrf_token()

        self.assertNotEqual(csrf, "")

    def create_feeded_parser_of(self, page: Webpage) -> HTMLParser:
        response = get_html_response_of(page)
        parser = create_parser_of(page)
        parser.feed(response.text)
        return parser


def get_html_response_of(type: Webpage) -> requests.Response:
    if type == Webpage.PROBLEM_CATEGORY:
        return requests.get("https://acmicpc.net/step")
    elif type == Webpage.PROBLEM_LIST:
        return requests.get("https://acmicpc.net/step/1")
    elif type == Webpage.PROBLEM:
        return requests.get("https://acmicpc.net/problem/2557")
    elif type == Webpage.SUBMIT:
        boj_cookies = browser_cookie3.chrome(domain_name="acmicpc.net")
        return requests.get("https://acmicpc.net/submit/2557", cookies=boj_cookies)


def create_parser_of(type: Webpage) -> HTMLParser:
    if type == Webpage.PROBLEM_CATEGORY:
        return ProblemCategoryParser()
    elif type == Webpage.PROBLEM_LIST:
        return ProblemListParser()
    elif type == Webpage.PROBLEM:
        return ProblemParser()
    elif type == Webpage.SUBMIT:
        return CSRFTokenParser()


if __name__ == "__main__":
    unittest.main()
