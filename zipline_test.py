import unittest
import zipline

from unittest.mock import patch
from zipline import (
    CodeOpenSelection,
    get_code_open_selection_from_user,
    get_source_and_language,
    Language,
    prepare_post_form,
)


class PostRequestPreparationTestcase(unittest.TestCase):
    def test_should_determine_golfscript_language_for_golfscript_file(self):
        source_info = get_source_and_language("./testcase/golfscript.gs")
        self.assertEqual(source_info.language, Language.GolfScript)
        self.assertNotEqual(source_info.content, "")

    def test_should_pick_user_preferred_c_language_when_multiple_choices_are_available_in_c_family(
        self,
    ):
        # Selection is sorted in ascending order, so the first selection must be C99.
        with patch.object(zipline, "input", return_value="0"):
            source_info = get_source_and_language("./testcase/c_file.c")
            self.assertEqual(source_info.language, Language.C99)
            self.assertNotEqual(source_info.content, "")

    def test_should_get_open_code_selection_when_user_says_make_code_open(self):
        with patch.object(zipline, "input", return_value="0"):
            open_selection = get_code_open_selection_from_user()
            self.assertEqual(open_selection, CodeOpenSelection.OPEN)

    def test_prepared_form_must_be_correct(self):
        with patch.object(zipline, "input", return_value="0"):
            form = prepare_post_form(1000, "helloworld.c")
            self.assertEqual(form.problem_id, 1000)
            self.assertEqual(form.language, Language.C99)
            self.assertEqual(form.code_open, CodeOpenSelection.OPEN)
            self.assertNotEqual(form.source, "")
            self.assertNotEqual(form.csrf_key, "")


if __name__ == "__main__":
    unittest.main()
