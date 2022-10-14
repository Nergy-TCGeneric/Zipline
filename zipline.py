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
class QueryType(IntEnum):
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
    C99 = 0
    CLANG_C99 = 59
    C11 = 75
    CLANG_C11 = 77
    CSharp = 86
    CPP11 = 49
    CLANG_CPP11 = 66
    CPP17 = 85
    Python2 = 6
    Python3 = 28
    PyPy2 = 32
    PyPy3 = 73
    Java8 = 3
    Java11 = 93
    Java15 = 107
    Kotlin = 69
    GolfScript = 79


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


def query_request(qtype: QueryType, id: int = -1) -> Response:
    boj_cookie = browser_cookie3.chrome(domain_name="acmicpc.net")

    if qtype == QueryType.PROBLEM:
        req = requests.get(f"https://acmicpc.net/problem/{id}", cookies=boj_cookie)
    elif qtype == QueryType.PROBLEM_LIST:
        req = requests.get(f"https://acmicpc.net/step/{id}", cookies=boj_cookie)
    elif qtype == QueryType.PROBLEM_CATEGORY:
        req = requests.get(f"https://acmicpc.net/step", cookies=boj_cookie)
    elif qtype == QueryType.SUBMIT:
        req = requests.get(f"https://acmicpc.net/submit/{id}", cookies=boj_cookie)

    if req.status_code == 404:
        raise Exception("no such content with given id")
    return req


def print_usage():
    print("Usage: zipline (-c (id) | -l (id) | -p <id>) (-s <id> <file path>) -i")


def print_problem_lists(id: int):
    try:
        req = query_request(QueryType.PROBLEM_LIST, id)
        previews = extract_all_problem_previews(req.text)

        for i in range(0, len(previews)):
            print(
                f"{i+1} {previews[i].title}({previews[i].id}) - {previews[i].accepted_submits}/{previews[i].submits}"
            )
    except:
        print("no such problem list with given id")


def print_problem_categories(id: int):
    try:
        req = query_request(QueryType.PROBLEM_CATEGORY, id)
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
        req = query_request(QueryType.PROBLEM, id)
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

        req = query_request(QueryType.SUBMIT, id)
        form.csrf_key = extract_csrf_token(req.text)

        source_info = get_source_and_language(filename)
        form.language = source_info.language
        form.source = source_info.content

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


def get_source_and_language(file_path: str) -> SourceFileInfo:
    path = Path(file_path)
    inferred_lang = infer_language_from_extension(path.suffix)

    with path.open() as f:
        content = f.read()
        return SourceFileInfo(inferred_lang, content)


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


def infer_language_from_extension(ext: str) -> Language:
    # TODO: By using file extension, if multiple choices are available then prompt user input to select one of them.
    # By now, this returns stub value instead.

    if ext == ".c":
        return Language.C99
    elif ext == ".gs":
        return Language.GolfScript
    elif ext == ".cc":
        return Language.CPP11
    elif ext == ".py":
        return Language.Python3
    elif ext == ".java":
        return Language.Java11
    elif ext == ".kt":
        return Language.Kotlin

    raise Exception(f"failed to infer language from given extension: {ext}")


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
