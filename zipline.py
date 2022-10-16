"""
    Zipline
    For who even don't want to open gui browsers just to do tedious works
"""

import json
import math
import os
import sys

from pathlib import Path
from enum import IntEnum, unique
from string import Template

import browser_cookie3
import requests
import websocket
from requests import Response

from html_extractors import (
    extract_all_problem_categories,
    extract_all_problem_previews,
    extract_csrf_token,
    extract_problem_detail,
    extract_submit_lists,
)

VERSION = "0.3.0"
STEP = -1
PUSHER_TOKEN = "a2cb611847131e062b32"
PADDING = 8


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


class SourceFileInfo:
    language: Language
    content: str

    def __init__(self, lang: Language, content: str) -> None:
        self.language = lang
        self.content = content


def get_webpage_of(wtype: Webpage, id: int = -1) -> Response:
    boj_cookie = browser_cookie3.chrome(domain_name="acmicpc.net")

    if wtype == Webpage.PROBLEM:
        req = requests.get(f"https://acmicpc.net/problem/{id}", cookies=boj_cookie)
    elif wtype == Webpage.PROBLEM_LIST:
        req = requests.get(f"https://acmicpc.net/step/{id}", cookies=boj_cookie)
    elif wtype == Webpage.PROBLEM_CATEGORY:
        req = requests.get(f"https://acmicpc.net/step", cookies=boj_cookie)
    elif wtype == Webpage.SUBMIT:
        req = requests.get(f"https://acmicpc.net/submit/{id}", cookies=boj_cookie)

    if req.status_code == 404:
        raise Exception("no such content with given id")
    return req


def print_usage():
    print("Usage: zipline (-c (id) | -l (id) | -p <id>) (-s <id> <file path>) -i")


def print_problem_lists(id: int):
    try:
        req = get_webpage_of(Webpage.PROBLEM_LIST, id)
        previews = extract_all_problem_previews(req.text)

        for i in range(0, len(previews)):
            print(
                f"{i+1} {previews[i].title}({previews[i].id}) - {previews[i].accepted_submits}/{previews[i].submits}"
            )
    except:
        print("no such problem list with given id")


def print_problem_categories(id: int):
    try:
        req = get_webpage_of(Webpage.PROBLEM_CATEGORY, id)
        categories = extract_all_problem_categories(req.text)

        for category in categories:
            color = (
                "\033[32m"
                if category.solved_count == category.total_count
                else "\033[0m"
            )
            print(
                f"{color}{category.id} {category.title} - ({category.solved_count}/{category.total_count}) \033[0m"
            )
    except:
        print("no such problem category with given id")


def print_problem_details(id: int):
    try:
        req = get_webpage_of(Webpage.PROBLEM, id)
        detail = extract_problem_detail(req.text)

        template = Template(
            """
            $color $id ($title) $reset_color
            - $tlimit, $mem_limit 내로 해결해야 함
            - 현재 $submits 번 제출되었고, 그 중 $accepted_submits 개가 정답 처리됨
            
            문제:
            $desc

            입력:
            $input_desc

            출력:
            $output_desc
        """
        ).substitute(
            color="\033[32m" if detail.preview.is_accepted else "\033[0m",
            reset_color="\033[0m",
            id=detail.preview.id,
            title=detail.preview.title,
            desc=detail.description,
            input_desc=detail.input_desc,
            output_desc=detail.output_desc,
            tlimit=detail.time_limit,
            mem_limit=detail.memory_limit,
            submits=detail.preview.submits,
            accepted_submits=detail.preview.accepted_submits,
        )

        print(template)
    except:
        print("no such problem with given id")


def prepare_post_form(id: int, filename: str) -> SubmitForm:
    try:
        form = SubmitForm()
        form.problem_id = id

        req = get_webpage_of(Webpage.SUBMIT, id)
        form.csrf_key = extract_csrf_token(req.text)

        file_path = Path(filename)
        form.language = infer_language_from_file(file_path)
        form.source = get_source_from(file_path)

        form.code_open = get_code_open_selection_from_user()
        return form
    except:
        print("no such problem with given id.")


def submit_solution(form: SubmitForm) -> int:
    boj_cookie = browser_cookie3.chrome(domain_name="acmicpc.net")
    res = requests.post(
        url=f"https://www.acmicpc.net/submit/{form.problem_id}",
        cookies=boj_cookie,
        data=form.to_dict(),
    )

    submit_list = extract_submit_lists(res.text)
    return submit_list[0].solution_id


def show_judge_progress(submit_id: int):
    subscriber = create_judge_result_subscriber(submit_id)
    judge_progress = JudgeProgress()
    print(f"{submit_id}번 제출 - 채점 준비중..")

    while not judge_progress.is_judge_ended():
        progress_json = receive_progress_from(socket=subscriber)
        judge_progress.renew_progress_from(progress_json)

        color = judge_progress.get_text_color()
        show_progress_bar(judge_progress.percentage, color)

    show_final_judge_result(judge_progress)


def create_judge_result_subscriber(submit_id: int) -> websocket.WebSocket:
    # Assuming judging servers have enough delay(> 500ms) to let our websocket client get entire content from beginning
    ws = websocket.WebSocket()
    ws.connect(
        f"wss://ws-ap1.pusher.com/app/{PUSHER_TOKEN}?protocol=7&client=js&version=4.2.2&flash=false"
    )
    ws.send(
        '{"event":"pusher:subscribe", "data":{"channel":"solution-%i"}}' % submit_id
    )
    return ws


def receive_progress_from(socket: websocket.WebSocket) -> any:
    received = socket.recv()
    # Because received json contains json object 'literal', we need to make it as an actual object
    replaced = received.replace("\\", "").replace('"{', "{").replace('}"', "}")
    return json.loads(replaced)


def show_progress_bar(progress: int, color: int):
    term_size = os.get_terminal_size()
    print(f"\033[{color}m", end="")

    prog_bar_width = math.floor((term_size.columns - PADDING) * progress / 100)
    progress_bar = "\r{0:<{pad}}{1}".format(
        f"{progress}%", "▓" * prog_bar_width, pad=PADDING
    )
    print(progress_bar, end="")


def get_source_from(file_path: Path) -> str:
    with file_path.open() as f:
        content = f.read()
        return content


def infer_language_from_file(file_path: Path) -> Language:
    candidates = get_candidates_from_extension(file_path.suffix)

    if len(candidates) > 1:
        selected = prompt_user_select_languages(candidates)
        return selected
    elif len(candidates) == 1:
        return candidates[0]
    else:
        # This is unreachable, since `get_candidates_from_extension` raises Exception if it failed to find candidates, making code fail early.
        pass


def prompt_user_select_languages(candidates: list[Language]) -> Language:
    pass


def get_code_open_selection_from_user() -> CodeOpenSelection:
    while True:
        print("코드를 공개할까요?")
        selection = input("공개 (0), 비공개 (1), 맞았을 때만 공개 (2): ")

        if not selection.isdigit():
            continue

        int_selection = int(selection)
        if int_selection < 0 or int_selection > 2:
            continue

        return CodeOpenSelection(int_selection)


def get_candidates_from_extension(ext: str) -> list[Language]:
    # TODO: By using file extension, if multiple choices are available then prompt user input to select one of them.
    # By now, this returns stub value instead.

    candidates = []

    if ext == ".c":
        candidates.append(Language.C99)
    elif ext == ".gs":
        candidates.append(Language.GolfScript)
    elif ext == ".cc":
        candidates.append(Language.CPP11)
    elif ext == ".py":
        candidates.append(Language.Python2)
    elif ext == ".java":
        candidates.append(Language.Java11)
    elif ext == ".kt":
        candidates.append(Language.Kotlin)
    else:
        raise Exception(f"failed to infer language from given extension: {ext}")

    return candidates


def show_final_judge_result(progress: JudgeProgress):
    # Adding a newline for prettier print
    print()

    if progress.result == JudgeResult.ACCEPTED:
        print(
            f"{progress.result} - {progress.consumed_memory_in_kb}KB 사용, {progress.consumed_time_in_ms}ms 경과함"
        )
    else:
        print(progress.result)


def parse_commands(argv: list[str]):
    for i in range(0, len(argv)):
        if argv[i] == "-c":
            if i < len(argv) - 1 and argv[i + 1].isnumeric():
                print_problem_categories(int(argv[i + 1]))
            else:
                print_problem_categories(STEP)
        elif argv[i] == "-l":
            if i < len(argv) - 1 and argv[i + 1].isnumeric():
                print_problem_lists(int(argv[i + 1]))
            else:
                print("id must be specified")
                print_usage()
        elif argv[i] == "-p":
            if i < len(argv) - 1 and argv[i + 1].isnumeric():
                print_problem_details(int(argv[i + 1]))
            else:
                print("id must be specified")
                print_usage()
        elif argv[i] == "-s":
            if i < len(argv) - 2 and argv[i + 1].isnumeric():
                postform = prepare_post_form(int(argv[i + 1]), argv[i + 2])
                submit_id = submit_solution(postform)
                show_judge_progress(submit_id)
            else:
                print("id and filename must be specified")
                print_usage()


if __name__ == "__main__":
    if len(sys.argv) - 1 == 0:
        print(f"Zipline {VERSION} - A TUI for BOJ")
        print_usage()
        sys.exit()

    parse_commands(sys.argv)
