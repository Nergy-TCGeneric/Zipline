from enum import IntEnum, unique


@unique
class TextColor(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97

    def get_foreground_color(self) -> int:
        return self.value


@unique
class Webpage(IntEnum):
    PROBLEM = 1
    PROBLEM_LIST = 2
    PROBLEM_CATEGORY = 3
    SUBMIT = 4


@unique
class JudgeResult(IntEnum):
    PENDING_JUDGE = 0
    PENDING_REJUDGE = 1
    PREPARING_JUDGE = 2
    JUDGING = 3
    ACCEPTED = 4
    PRESENTATION_ERROR = 5
    WRONG_ANSWER = 6
    TIME_EXCEEDED = 7
    MEMORY_EXCEEDED = 8
    OUTPUT_EXCEEDED = 9
    RUNTIME_ERROR = 10
    COMPILE_ERROR = 11
    UNAVAILABLE = 12
    PARTIALLY_ACCEPTED = 15

    def __str__(self) -> str:
        if self == JudgeResult.PENDING_JUDGE:
            return "기다리는 중"
        elif self == JudgeResult.PENDING_REJUDGE:
            return "재채점을 기다리는 중"
        elif self == JudgeResult.PREPARING_JUDGE:
            return "채점 준비 중"
        elif self == JudgeResult.JUDGING:
            return "채점 중"
        elif self == JudgeResult.ACCEPTED:
            return "맞았습니다!"
        elif self == JudgeResult.PRESENTATION_ERROR:
            return "출력 형식이 잘못되었습니다"
        elif self == JudgeResult.WRONG_ANSWER:
            return "틀렸습니다"
        elif self == JudgeResult.TIME_EXCEEDED:
            return "시간 초과"
        elif self == JudgeResult.MEMORY_EXCEEDED:
            return "메모리 초과"
        elif self == JudgeResult.OUTPUT_EXCEEDED:
            return "출력 초과"
        elif self == JudgeResult.RUNTIME_ERROR:
            return "런타임 오류"
        elif self == JudgeResult.COMPILE_ERROR:
            return "컴파일 오류"
        elif self == JudgeResult.UNAVAILABLE:
            return "채점 불가능"
        elif self == JudgeResult.PARTIALLY_ACCEPTED:
            return "일부만 맞았습니다!"
        else:
            raise Exception(f"not implemented for given value: {self.value}")


@unique
class Language(IntEnum):
    C90 = 101
    CLANG_C90 = 103
    C99 = 0
    CLANG_C99 = 59
    C11 = 75
    CLANG_C11 = 77
    C2x = 102
    CLANG_C2x = 104

    CPP98 = 1
    CLANG_CPP98 = 60
    CPP11 = 49
    CLANG_CPP11 = 66
    CPP14 = 88
    CLANG_CPP14 = 67
    CPP17 = 84
    CLANG_CPP17 = 85
    CPP20 = 95
    CLANG_CPP20 = 96

    CSharp = 86
    CSharp_3_Mono = 9
    CSharp_6_Mono = 62

    Python2 = 6
    Python3 = 28
    PyPy2 = 32
    PyPy3 = 73
    Haxe = 81

    Java8 = 3
    Java8_OpenJDK = 91
    Java11 = 93
    Java15 = 107

    Kotlin_JVM = 69
    Kotlin_Native = 92

    Rust_2015 = 44
    Rust_2018 = 94
    Rust_2021 = 113

    D = 29
    D_LDC = 100

    FSharp = 108
    FSharp_Mono = 37

    Ruby = 68
    Ruby_18 = 4
    Ruby_19 = 65

    Go = 12
    Go_GCC = 90

    NodeJs = 17
    TypeScript = 106
    Rhino = 34

    VB_NET_2_Mono = 20
    VB_NET_4_Mono = 63
    VisualBasic = 109

    Assembly_32bit = 27
    Assembly_64bit = 87

    PHP = 7
    Haskell = 11
    Text = 58
    GolfScript = 79
    Pascal = 2
    Scala = 15
    Lua = 16
    Perl = 8
    Bash = 5
    Fortran = 13
    Scheme = 14
    Ada = 19
    awk = 21
    OCaml = 22
    BrainFuck = 23
    Whitespace = 24
    Tcl = 26
    Cobol = 35
    Pike = 41
    sed = 43
    Boo = 46
    FreeBASIC = 78
    Swift = 74
    Objective_C = 10
    Objective_CPP = 64
    INTERCAL = 47
    bc = 48
    Nemerle = 53
    Cobra = 54
    Nimrod = 55
    Algol_68 = 70
    Befunge = 71
    LOLCODE = 82
    Aheui = 83
    Coq = 98
    Minecraft = 99
    SystemVerilog = 105
    APECODE = 110
    Crystal = 111
    Umjunsik = 112

    def get_file_extension(self) -> str:
        if self in [
            Language.C90,
            Language.CLANG_C90,
            Language.C99,
            Language.CLANG_C99,
            Language.C11,
            Language.CLANG_C11,
            Language.C2x,
            Language.CLANG_C2x,
        ]:
            return ".c"

        elif self in [
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
        ]:
            return ".cc"

        elif self in [Language.CSharp, Language.CSharp_3_Mono, Language.CSharp_6_Mono]:
            return ".cs"

        elif self in [
            Language.Python2,
            Language.Python3,
            Language.PyPy2,
            Language.PyPy3,
            Language.Haxe,
        ]:
            return ".py"

        elif self in [
            Language.Java8,
            Language.Java8_OpenJDK,
            Language.Java11,
            Language.Java15,
        ]:
            return ".java"

        elif self in [Language.Kotlin_JVM, Language.Kotlin_Native]:
            return ".kt"

        elif self in [Language.Rust_2015, Language.Rust_2018, Language.Rust_2021]:
            return ".rs"

        elif self in [Language.D, Language.D_LDC]:
            return ".d"

        elif self in [Language.FSharp, Language.FSharp_Mono]:
            return ".fs"

        elif self in [Language.Ruby, Language.Ruby_18, Language.Ruby_19]:
            return ".rb"

        elif self in [Language.Go, Language.Go_GCC]:
            return ".go"

        elif self in [Language.NodeJs, Language.TypeScript, Language.Rhino]:
            return ".js"

        elif self in [
            Language.VB_NET_2_Mono,
            Language.VB_NET_4_Mono,
            Language.VisualBasic,
        ]:
            return ".vb"

        elif self in [Language.Assembly_32bit, Language.Assembly_64bit]:
            return ".asm"

        elif self == Language.PHP:
            return ".php"
        elif self == Language.Haskell:
            return ".hs"
        elif self == Language.Text:
            return ".txt"
        elif self == Language.GolfScript:
            return ".gs"
        elif self == Language.Pascal:
            return ".pas"
        elif self == Language.Scala:
            return ".scala"
        elif self == Language.Lua:
            return ".lua"
        elif self == Language.Perl:
            return ".pl"
        elif self == Language.Bash:
            return ".sh"
        elif self == Language.Fortran:
            return ".f95"
        elif self == Language.Scheme:
            return ".scm"
        elif self == Language.Ada:
            return ".ada"
        elif self == Language.awk:
            return ".awk"
        elif self == Language.OCaml:
            return ".ml"
        elif self == Language.BrainFuck:
            return ".bf"
        elif self == Language.Whitespace:
            return ".ws"
        elif self == Language.Tcl:
            return ".tcl"
        elif self == Language.Cobol:
            return ".cob"
        elif self == Language.Pike:
            return ".pike"
        elif self == Language.sed:
            return ".sed"
        elif self == Language.Boo:
            return ".boo"
        elif self == Language.FreeBASIC:
            return ".bas"
        elif self == Language.Swift:
            return ".swift"
        elif self == Language.Objective_C:
            return ".m"
        elif self == Language.Objective_CPP:
            return ".mm"
        elif self == Language.INTERCAL:
            return ".i"
        elif self == Language.bc:
            return ".bc"
        elif self == Language.Nemerle:
            return ".n"
        elif self == Language.Cobra:
            return ".cobra"
        elif self == Language.Nimrod:
            return ".nim"
        elif self == Language.Algol_68:
            return ".a68"
        elif self == Language.Befunge:
            return ".bf"
        elif self == Language.LOLCODE:
            return ".lol"
        elif self == Language.Aheui:
            return ".aheui"
        elif self == Language.Coq:
            return ".v"
        elif self == Language.Minecraft:
            return ".mca"
        elif self == Language.SystemVerilog:
            return ".sv"
        elif self == Language.APECODE:
            return ".ape"
        elif self == Language.Crystal:
            return ".cr"
        elif self == Language.Umjunsik:
            return ".umm"

        raise Exception(f"can't find corresponding file extension for language: {self}")


@unique
class CodeOpenSelection(IntEnum):
    OPEN = 0
    CLOSE = 1
    ONLYACCEPTED = 2

    def __str__(self) -> str:
        if self == CodeOpenSelection.OPEN:
            return "open"
        elif self == CodeOpenSelection.CLOSE:
            return "close"
        elif self == CodeOpenSelection.ONLYACCEPTED:
            return "onlyaccepted"


class JudgeProgress:
    consumed_memory_in_kb: int = 0
    consumed_time_in_ms: int = 0
    percentage: int = 0
    result: JudgeResult = JudgeResult.PENDING_JUDGE

    def renew_progress_from(self, json: dict):
        if json["event"] != "update":
            return

        if "result" in json["data"]:
            self.result = JudgeResult(int(json["data"]["result"]))
        if "progress" in json["data"]:
            self.percentage = int(json["data"]["progress"])
        if "memory" in json["data"]:
            self.consumed_memory_in_kb = int(json["data"]["memory"])
        if "time" in json["data"]:
            self.consumed_time_in_ms = int(json["data"]["time"])

    def is_judge_ended(self) -> bool:
        return self.result > JudgeResult.JUDGING.value

    def get_text_color(self) -> TextColor:
        if self.result == JudgeResult.PENDING_JUDGE:
            return TextColor.BRIGHT_BLACK
        elif self.result == JudgeResult.PENDING_REJUDGE:
            return TextColor.BRIGHT_BLACK
        elif self.result == JudgeResult.PREPARING_JUDGE:
            return TextColor.WHITE
        elif self.result == JudgeResult.JUDGING:
            return TextColor.WHITE
        elif self.result == JudgeResult.ACCEPTED:
            return TextColor.GREEN
        elif self.result == JudgeResult.PRESENTATION_ERROR:
            return TextColor.BRIGHT_RED
        elif self.result == JudgeResult.WRONG_ANSWER:
            return TextColor.RED
        elif self.result == JudgeResult.TIME_EXCEEDED:
            return TextColor.BRIGHT_RED
        elif self.result == JudgeResult.MEMORY_EXCEEDED:
            return TextColor.BRIGHT_RED
        elif self.result == JudgeResult.OUTPUT_EXCEEDED:
            return TextColor.BRIGHT_RED
        elif self.result == JudgeResult.RUNTIME_ERROR:
            return TextColor.BRIGHT_MAGENTA
        elif self.result == JudgeResult.COMPILE_ERROR:
            return TextColor.BRIGHT_MAGENTA
        elif self.result == JudgeResult.UNAVAILABLE:
            return TextColor.BRIGHT_BLACK
        elif self.result == JudgeResult.PARTIALLY_ACCEPTED:
            return TextColor.BRIGHT_YELLOW


class SubmitForm:
    problem_id: int
    language: Language
    code_open: CodeOpenSelection
    source: str
    csrf_key: str

    def __init__(self) -> None:
        self.problem_id = 0
        self.language = Language.C99
        self.code_open = CodeOpenSelection.OPEN
        self.source = ""
        self.csrf_key = ""

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "language": self.language.value,
            "code_open": str(self.code_open),
            "source": self.source,
            "csrf_key": self.csrf_key,
        }


class ContentNotFound(Exception):
    def __init__(self):
        super()
