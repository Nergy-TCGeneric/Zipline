
'''
    Zipline
    For who even don't want to open gui browsers just to do tedious works
'''

import sys
import os
import requests
import browser_cookie3
import websocket
import json
import math

from collections import namedtuple
from enum import IntEnum, unique
from requests import get, Response, Request, Session
from html_extractors import extract_all_problem_categories, extract_all_problem_previews, extract_csrf_token, extract_problem_detail, extract_submit_lists
from string import Template

VERSION = "0.3.0"
STEP = -1
PUSHER_TOKEN = "a2cb611847131e062b32"
PADDING = 8

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
        if self.value == 0:
            return "기다리는 중"
        elif self.value == 1:
            return "재채점을 기다리는 중"
        elif self.value == 2:
            return "채점 준비 중"
        elif self.value == 3:
            return "채점 중"
        elif self.value == 4:
            return "맞았습니다!"
        elif self.value == 5:
            return "출력 형식이 잘못되었습니다"
        elif self.value == 6:
            return "틀렸습니다"
        elif self.value == 7:
            return "시간 초과"
        elif self.value == 8:
            return "메모리 초과"
        elif self.value == 9:
            return "출력 초과"
        elif self.value == 10:
            return "런타임 오류"
        elif self.value == 11:
            return "컴파일 오류"
        elif self.value == 12:
            return "채점 불가능"
        elif self.value == 15:
            return "일부만 맞았습니다!"
        else:
            raise Exception(f"not implemented for given value: {self.value}")

class JudgeProgress:
    consumed_memory_in_kb: int = 0
    consumed_time_in_ms: int = 0
    percentage: int = 0
    result: JudgeResult = JudgeResult.PENDING_JUDGE

    def renew_progress_from(self, json: dict):
        if json['event'] != 'update':
            return
        
        if 'result' in json['data']:
            self.result = JudgeResult(int(json['data']['result']))
        if 'progress' in json['data']:
            self.percentage = int(json['data']['progress'])
        if 'memory' in json['data']:
            self.consumed_memory_in_kb = int(json['data']['memory'])
        if 'time' in json['data']:
            self.consumed_time_in_ms = int(json['data']['time'])

    def is_judge_ended(self) -> bool:
        return self.result > JudgeResult.JUDGING.value

    def get_text_color(self) -> int:
        if self.result.value == 0:
            return 90
        elif self.result.value == 1:
            return 90
        elif self.result.value == 2:
            return 37
        elif self.result.value == 3:
            return 37
        elif self.result.value == 4:
            return 32
        elif self.result.value == 5:
            return 91
        elif self.result.value == 6:
            return 31
        elif self.result.value == 7:
            return 91
        elif self.result.value == 8:
            return 91
        elif self.result.value == 9:
            return 91
        elif self.result.value == 10:
            return 95
        elif self.result.value == 11:
            return 95
        elif self.result.value == 12:
            return 90
        elif self.result.value == 15:
            return 93
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
        raise Exception('no such content with given id')
    return req

def print_usage():
    print("Usage: zipline (-c (id) | -l (id) | -p <id>) (-s <id> <file path>) -i")

def print_problem_lists(id: int):
    try:
        req = query_request(QueryType.PROBLEM_LIST, id)
        previews = extract_all_problem_previews(req.text)

        for i in range(0, len(previews)):
            print(f"{i+1} {previews[i].title}({previews[i].id}) - {previews[i].accepted_submits}/{previews[i].submits}")
    except:
        print("no such problem list with given id")

def print_problem_categories(id: int):
    try:
        req = query_request(QueryType.PROBLEM_CATEGORY, id)
        categories = extract_all_problem_categories(req.text)

        for category in categories:
            color = "\033[32m" if category.solved_count == category.total_count else "\033[0m"
            print(f"{color}{category.id} {category.title} - ({category.solved_count}/{category.total_count}) \033[0m")
    except:
        print("no such problem category with given id")

def print_problem_details(id: int):
    try:
        req = query_request(QueryType.PROBLEM, id)
        detail = extract_problem_detail(req.text)

        template = Template("""
            $color $id ($title) $reset_color
            - $tlimit, $mem_limit 내로 해결해야 함
            - 현재 $submits 번 제출되었고, 그 중 $accepted_submits 개가 정답 처리됨
            
            문제:
            $desc

            입력:
            $input_desc

            출력:
            $output_desc
        """).substitute(
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
            accepted_submits=detail.preview.accepted_submits
        )

        print(template)
    except:
        print('no such problem with given id')

def submit_solution(id: int, filename: str) -> int:
    try:
        req = query_request(QueryType.SUBMIT, id)
        csrf_token = extract_csrf_token(req.text)
        form = craft_submit_form(id, filename, csrf_token)

        boj_cookie = browser_cookie3.chrome(domain_name="acmicpc.net")
        res = requests.post(url=f"https://www.acmicpc.net/submit/{id}", cookies=boj_cookie, data=form)

        submit_list = extract_submit_lists(res.text)
        return submit_list[0].solution_id
    except:
        print("no such problem with given id.")

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
    ws.connect(f"wss://ws-ap1.pusher.com/app/{PUSHER_TOKEN}?protocol=7&client=js&version=4.2.2&flash=false")
    ws.send('{"event":"pusher:subscribe", "data":{"channel":"solution-%i"}}' % submit_id)
    return ws

def receive_progress_from(socket: websocket.WebSocket) -> any:
    received = socket.recv()
    # Because received json contains json object 'literal', we need to make it as an actual object
    replaced = received.replace('\\', '').replace("\"{", "{").replace("}\"", "}")
    return json.loads(replaced)

def show_progress_bar(progress: int, color: int):
    term_size = os.get_terminal_size()
    print(f'\033[{color}m', end='')

    prog_bar_width = math.floor((term_size.columns - PADDING) * progress / 100)
    progress_bar = '\r{0:<{pad}}{1}'.format(f"{progress}%", '▓' * prog_bar_width, pad=PADDING)
    print(progress_bar, end='')

def show_final_judge_result(progress: JudgeProgress):
    # Adding a newline for prettier print
    print()

    if progress.result == JudgeResult.ACCEPTED:
        print(f"{progress.result} - {progress.consumed_memory_in_kb}KB 사용, {progress.consumed_time_in_ms}ms 경과함")
    else:
        print(progress.result)

def craft_submit_form(id: int, filename: str, csrf_token: str) -> dict:
    # TODO: Load preference from somewhere and craft with everything.
    with open(filename) as source_file:
        src = source_file.read()
        form = {
            'problem_id': id,
            'language': 0,
            'code_open': 'close',
            'source': src,
            'csrf_key': csrf_token
        }

        return form

def parse_commands(argv: list[str]):
    for i in range(0, len(argv)):
        if argv[i] == "-c":
            if i < len(argv) - 1 and argv[i+1].isnumeric():
                print_problem_categories(int(argv[i+1]))
            else:
                print_problem_categories(STEP)
        elif argv[i] == "-l":
            if i < len(argv) - 1 and argv[i+1].isnumeric():
                print_problem_lists(int(argv[i+1]))
            else:
                print("id must be specified")
                print_usage()
        elif argv[i] == "-p":
            if i < len(argv) - 1 and argv[i+1].isnumeric():
                print_problem_details(int(argv[i+1]))
            else:
                print("id must be specified")
                print_usage()
        elif argv[i] == "-s":
            if i < len(argv) - 2 and argv[i+1].isnumeric():
                submit_id = submit_solution(int(argv[i+1]), argv[i+2])
                show_judge_progress(submit_id)
            else:
                print("id and filename must be specified")
                print_usage()

if __name__ == "__main__":
    if len(sys.argv)-1 == 0:
        print(f"Zipline {VERSION} - A TUI for BOJ")
        print_usage()
        sys.exit()

    parse_commands(sys.argv)