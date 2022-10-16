import unittest
import zipline

from pathlib import Path
from unittest.mock import patch
from zipline import (
    CodeOpenSelection,
    get_code_open_selection_from_user,
    infer_language_from_file,
    Language,
    prepare_post_form,
    get_candidates_from_extension,
)


class PostRequestPreparationTestcase(unittest.TestCase):
    def test_should_determine_golfscript_language_for_golfscript_file(self):
        lang = infer_language_from_file(Path("./testcase/golfscript.gs"))
        self.assertEqual(lang, Language.GolfScript)

    def test_should_pick_user_preferred_c_language_when_multiple_choices_are_available_in_c_family(
        self,
    ):
        # Selection is sorted in ascending order, so the first selection must be C99.
        with patch.object(zipline, "input", return_value="0"):
            lang = infer_language_from_file(Path("./testcase/c_file.c"))
            self.assertEqual(lang, Language.C99)

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


class LanguageFileExtensionEquivalenceTestcase(unittest.TestCase):
    def check_if_languages_share_equal_extensions(
        self, languages: list[Language], extension: str
    ):
        for lang in languages:
            self.assertEqual(lang.get_file_extension(), extension)

    def check_if_language_have_equal_extension(
        self, language: Language, extension: str
    ):
        self.assertEqual(language.get_file_extension(), extension)

    def test_all_c_variants_share_equal_file_extensions(self):
        C_VARIANTS = [
            Language.C90,
            Language.CLANG_C90,
            Language.C99,
            Language.CLANG_C99,
            Language.C11,
            Language.CLANG_C11,
            Language.C2x,
            Language.CLANG_C2x,
        ]

        self.check_if_languages_share_equal_extensions(C_VARIANTS, ".c")

    def test_all_cpp_variants_share_equal_file_extensions(self):
        CPP_VARIANTS = [
            Language.CPP98,
            Language.CLANG_CPP98,
            Language.CPP11,
            Language.CLANG_CPP11,
            Language.CPP14,
            Language.CLANG_CPP14,
            Language.CPP17,
            Language.CLANG_CPP17,
            Language.CPP20,
            Language.CLANG_CPP20,
        ]

        self.check_if_languages_share_equal_extensions(CPP_VARIANTS, ".cc")

    def test_all_csharp_variants_share_equal_file_extensions(self):
        # NOTE: C# is compiled by following arguments in BOJ. Assuming it have a default file extension '.cs'.
        # dotnet new console --force -o Main && dotnet publish Main --configuration Release --self-contained true --runtime linux-x64
        CSHARP_VARIANTS = [
            Language.CSharp,
            Language.CSharp_3_Mono,
            Language.CSharp_6_Mono,
        ]

        self.check_if_languages_share_equal_extensions(CSHARP_VARIANTS, ".cs")

    def test_all_python_variants_share_equal_file_extensions(self):
        PYTHON_VARIANTS = [
            Language.Python2,
            Language.Python3,
            Language.PyPy2,
            Language.PyPy3,
            Language.Haxe,
        ]

        self.check_if_languages_share_equal_extensions(PYTHON_VARIANTS, ".py")

    def test_all_java_variants_share_equal_file_extensions(self):
        JAVA_VARIANTS = [
            Language.Java8,
            Language.Java8_OpenJDK,
            Language.Java11,
            Language.Java15,
        ]

        self.check_if_languages_share_equal_extensions(JAVA_VARIANTS, ".java")

    def test_all_kotlin_variants_share_equal_file_extensions(self):
        KOTLIN_VARIANTS = [Language.Kotlin_JVM, Language.Kotlin_Native]

        self.check_if_languages_share_equal_extensions(KOTLIN_VARIANTS, ".kt")

    def test_all_rust_variants_share_equal_file_extensions(self):
        RUST_VARIANTS = [Language.Rust_2015, Language.Rust_2018, Language.Rust_2021]

        self.check_if_languages_share_equal_extensions(RUST_VARIANTS, ".rs")

    def test_all_d_variants_share_equal_file_extensions(self):
        D_VARIANTS = [Language.D, Language.D_LDC]

        self.check_if_languages_share_equal_extensions(D_VARIANTS, ".d")

    def test_all_f_variants_share_equal_file_extensions(self):
        # NOTE: Like C#, Assuming F# have a default file extension '.fs'.
        # In BOJ, F# is compiled by following arguments:
        # dotnet new console --language "F#" --force -o Main && dotnet publish Main --configuration Release --self-contained true --runtime linux-x64
        F_VARIANTS = [Language.FSharp, Language.FSharp_Mono]

        self.check_if_languages_share_equal_extensions(F_VARIANTS, ".fs")

    def test_all_ruby_variants_share_equal_file_extensions(self):
        RUBY_VARIANTS = [Language.Ruby, Language.Ruby_18, Language.Ruby_19]

        self.check_if_languages_share_equal_extensions(RUBY_VARIANTS, ".rb")

    def test_all_go_variants_share_equal_file_extensions(self):
        GO_VARIANTS = [Language.Go, Language.Go_GCC]

        self.check_if_languages_share_equal_extensions(GO_VARIANTS, ".go")

    def test_all_javascript_variants_share_equal_file_extensions(self):
        JS_VARIANTS = [Language.NodeJs, Language.TypeScript, Language.Rhino]

        self.check_if_languages_share_equal_extensions(JS_VARIANTS, ".js")

    def test_all_basic_variants_share_equal_file_extensions(self):
        # NOTE: Assuming VisualBasic have a default file extension '.vb'
        BASIC_VARIANTS = [
            Language.VB_NET_2_Mono,
            Language.VB_NET_4_Mono,
            Language.VisualBasic,
        ]

        self.check_if_languages_share_equal_extensions(BASIC_VARIANTS, ".vb")

    def test_all_assembly_variants_share_equal_file_extensions(self):
        ASM_VARIANTS = [Language.Assembly_32bit, Language.Assembly_64bit]

        self.check_if_languages_share_equal_extensions(ASM_VARIANTS, ".asm")

    def test_all_other_languages_matches_their_own_file_extensions(self):
        self.check_if_language_have_equal_extension(Language.PHP, ".php")
        self.check_if_language_have_equal_extension(Language.Haskell, ".hs")
        self.check_if_language_have_equal_extension(Language.Text, ".txt")
        self.check_if_language_have_equal_extension(Language.GolfScript, ".gs")
        self.check_if_language_have_equal_extension(Language.Pascal, ".pas")
        self.check_if_language_have_equal_extension(Language.Scala, ".scala")
        self.check_if_language_have_equal_extension(Language.Lua, ".lua")
        self.check_if_language_have_equal_extension(Language.Perl, ".pl")
        self.check_if_language_have_equal_extension(Language.Bash, ".sh")
        self.check_if_language_have_equal_extension(Language.Fortran, ".f95")
        self.check_if_language_have_equal_extension(Language.Scheme, ".scm")
        self.check_if_language_have_equal_extension(Language.Ada, ".ada")
        self.check_if_language_have_equal_extension(Language.awk, ".awk")
        self.check_if_language_have_equal_extension(Language.OCaml, ".ml")
        self.check_if_language_have_equal_extension(Language.Whitespace, ".ws")
        self.check_if_language_have_equal_extension(Language.Tcl, ".tcl")
        self.check_if_language_have_equal_extension(Language.Cobol, ".cob")
        self.check_if_language_have_equal_extension(Language.Pike, ".pike")
        self.check_if_language_have_equal_extension(Language.sed, ".sed")
        self.check_if_language_have_equal_extension(Language.Boo, ".boo")
        self.check_if_language_have_equal_extension(Language.FreeBASIC, ".bas")
        self.check_if_language_have_equal_extension(Language.Swift, ".swift")
        self.check_if_language_have_equal_extension(Language.Objective_C, ".m")
        self.check_if_language_have_equal_extension(Language.Objective_CPP, ".mm")
        self.check_if_language_have_equal_extension(Language.INTERCAL, ".i")
        self.check_if_language_have_equal_extension(Language.bc, ".bc")
        self.check_if_language_have_equal_extension(Language.Nemerle, ".n")
        self.check_if_language_have_equal_extension(Language.Cobra, ".cobra")
        self.check_if_language_have_equal_extension(Language.Nimrod, ".nim")
        self.check_if_language_have_equal_extension(Language.Algol_68, ".a68")
        self.check_if_language_have_equal_extension(Language.LOLCODE, ".lol")
        self.check_if_language_have_equal_extension(Language.Aheui, ".aheui")
        self.check_if_language_have_equal_extension(Language.Minecraft, ".mca")
        self.check_if_language_have_equal_extension(Language.SystemVerilog, ".sv")
        self.check_if_language_have_equal_extension(Language.APECODE, ".ape")
        self.check_if_language_have_equal_extension(Language.Crystal, ".cr")
        self.check_if_language_have_equal_extension(Language.Umjunsik, ".umm")

        # NOTE: See https://stackoverflow.com/questions/7963528/what-does-v-stand-for-in-the-coq-file-extension, might be inaccurate
        self.check_if_language_have_equal_extension(Language.Coq, ".v")

        # NOTE: They are totally different, but accidentally they have a same extensions.
        self.check_if_language_have_equal_extension(Language.BrainFuck, ".bf")
        self.check_if_language_have_equal_extension(Language.Befunge, ".bf")

    def test_should_return_multiple_languages_that_share_same_file_extensions(self):
        C_VARIANTS = [
            Language.C90,
            Language.CLANG_C90,
            Language.C99,
            Language.CLANG_C99,
            Language.C11,
            Language.CLANG_C11,
            Language.C2x,
            Language.CLANG_C2x,
        ]

        langs = get_candidates_from_extension(".c")
        for l in langs:
            self.assertTrue(l in C_VARIANTS)


if __name__ == "__main__":
    unittest.main()
