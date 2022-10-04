
'''
    Zipline
    For who even don't want to open gui browsers just to do tedious works
'''

import sys
import os
import browser_cookie3
import websocket
import json
import math

from collections import namedtuple
from enum import IntEnum, unique
from requests import get, Response, Request, Session
from boj_parsers import *
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
    PRESENTATION_ERROR = 5,
    WRONG_ANSWER = 6,
    TIME_EXCEEDED = 7,
    MEMORY_EXCEEDED = 8,
    OUTPUT_EXCEEDED = 9,
    RUNTIME_ERROR = 10,
    COMPILE_ERROR = 11,
    UNAVAILABLE = 12,
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

    def get_color_code(self) -> int:
        if self.value == 0:
            return 90
        elif self.value == 1:
            return 90
        elif self.value == 2:
            return 37
        elif self.value == 3:
            return 37
        elif self.value == 4:
            return 32
        elif self.value == 5:
            return 91
        elif self.value == 6:
            return 31
        elif self.value == 7:
            return 91
        elif self.value == 8:
            return 91
        elif self.value == 9:
            return 91
        elif self.value == 10:
            return 95
        elif self.value == 11:
            return 95
        elif self.value == 12:
            return 90
        elif self.value == 15:
            return 93
        else:
            raise Exception(f"color code not implemented for {self.value}")

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
    
    return req

def print_usage():
    print("Usage: zipline (-c (id) | -l (id) | -p <id>) (-s <id> <file path>)")

def print_problem_lists(id: int):
    req = query_request(QueryType.PROBLEM_LIST, id)
    if req.status_code == 404:
        print("no such problem list with given id")
        return
    
    parser = ProblemListParser()
    parser.feed(req.text)
    previews = parser.get_all_problem_previews()

    for i in range(0, len(previews)):
        print(f"{i+1} {previews[i].title}({previews[i].id}) - {previews[i].accepted_submits}/{previews[i].submits}")

def print_problem_categories(id: int):
    req = query_request(QueryType.PROBLEM_CATEGORY, id)
    if req.status_code == 404:
        print("no such problem category with given id")
        return
    
    parser = ProblemCategoryParser()
    parser.feed(req.text)
    categories = parser.get_all_problem_category()

    for category in categories:
        color = "\033[32m" if category.solved_count == category.total_count else "\033[0m"
        print(f"{color}{category.id} {category.title} - ({category.solved_count}/{category.total_count}) \033[0m")

def print_problem_details(id: int):
    req = query_request(QueryType.PROBLEM, id)
    if req.status_code == 404:
        print("no such problem with given id")
        return
    
    parser = ProblemParser()
    parser.feed(req.text)
    detail = parser.get_problem_details()

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

def submit_solution(id: int, filename: str):
    req = query_request(QueryType.SUBMIT, id)
    if req.status_code == 404:
        print("no such problem with given id.")
        return
    
    csrf_parser = CSRFTokenParser()
    csrf_parser.feed(req.text)
    csrf_token = csrf_parser.get_csrf_token()

    boj_cookie = browser_cookie3.chrome(domain_name="acmicpc.net")

    with open(filename) as source_file:
        src = source_file.read()
        form = {
            'problem_id': id,
            'language': 0, # See https://help.acmicpc.net/language/info for details.
            'code_open': 'close',
            'source': src,
            'csrf_key': csrf_token
        }

        # Connect to websocket first
        ws = websocket.WebSocket()
        ws.connect(f"wss://ws-ap1.pusher.com/app/{PUSHER_TOKEN}?protocol=7&client=js&version=4.2.2&flash=false")
        
        res = requests.post(url=f"https://www.acmicpc.net/submit/{id}", cookies=boj_cookie, data=form)

        # Extract submit list(represented in js array) from response body
        start_index = res.text.find("solution_ids") + len("solution_ids = ")
        end_index = res.text.find(";", start_index)
        list_literal = res.text[start_index:end_index]

        submit_list = parse_submit_list_literal(list_literal)
        # To get a real-time progress, we need to subscribe channel first
        ws.send('{"event":"pusher:subscribe", "data":{"channel":"solution-%i"}}' % submit_list[0].solution_id)

        end_of_judge_range = range(4, 13)
        current_result = JudgeResult.PENDING_JUDGE
        prepared_text = ''

        print(f"{id}번 문제 - 채점 준비중..")
        while True:
            received = ws.recv()
            # Because received json contains json object 'literal', we need to make it as an actual object
            replaced = received.replace('\\', '').replace("\"{", "{").replace("}\"", "}")
            parsed = json.loads(replaced)

            if parsed['event'] == 'update':
                current_result = JudgeResult(int(parsed['data']['result']))

            # Prepare text color first
            term_size = os.get_terminal_size()
            color_code = current_result.get_color_code()
            print(f'\033[{color_code}m', end='')

            if 'progress' in parsed['data']:
                progress = int(parsed['data']['progress'])
                prog_bar_width = math.floor((term_size.columns - PADDING) * progress / 100)
                prepared_text = '\r{0:<{pad}}{1}'.format(f"{progress}%", '▓' * prog_bar_width, pad=PADDING)

            print(prepared_text, end='')
            if current_result in end_of_judge_range:
                break
        
        # Add a newline for prettier print
        print()
        print(current_result)

def parse_submit_list_literal(literal: str) -> list[namedtuple]:
    # From newest to oldest order
    parsed = []
    submit_list = literal.replace('[', '').replace(']', '').split(',')

    # Store everything into tuple except last element, as it's empty
    for i in range(0, len(submit_list) - 1, 2):
        submit_info = namedtuple('SubmitInfo', ['solution_id', 'status_code'])
        t = submit_info(int(submit_list[i]), int(submit_list[i+1]))
        parsed.append(t)
    
    return parsed

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
                submit_solution(int(argv[i+1]), argv[i+2])
            else:
                print("id and filename must be specified")
                print_usage()

if __name__ == "__main__":
    if len(sys.argv)-1 == 0:
        print(f"Zipline {VERSION} - A TUI for BOJ")
        print_usage()
        sys.exit()

    parse_commands(sys.argv)