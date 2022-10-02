
'''
    Zipline
    For who even don't want to open gui browsers just to do tedious works
'''

import sys
import browser_cookie3

from collections import namedtuple
from enum import Enum
from requests import get, Response, Request, Session
from boj_parsers import *
from string import Template

VERSION = "0.1.0"
STEP = -1

class QueryType(Enum):
    PROBLEM = 1
    PROBLEM_LIST = 2
    PROBLEM_CATEGORY = 3
    SUBMIT = 4

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

    with open(filename) as filedata:
        src = filedata.read()
        form = {
            'problem_id': id,
            'language': 0, # See https://help.acmicpc.net/language/info for details.
            'code_open': 'close',
            'source': src,
            'csrf_key': csrf_token
        }

        res = requests.post(url=f"https://www.acmicpc.net/submit/{id}", cookies=boj_cookie, data=form)

        start_index = res.text.find("solution_ids") + len("solution_ids = ")
        end_index = res.text.find(";", start_index)
        list_literal = res.text[start_index:end_index]

        submit_list = parse_submit_list_literal(list_literal)
        print(submit_list)

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