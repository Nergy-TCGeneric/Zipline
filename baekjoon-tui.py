
'''
    Baekjoon TUI
    For who even don't want to open gui browsers just to do tedious works
'''

import sys
from enum import Enum
from requests import get, Response
from boj_parsers import *
from string import Template

TUI_VERSION = "0.0.1"
STEP = -1

class QueryType(Enum):
    PROBLEM = 1
    PROBLEM_LIST = 2
    PROBLEM_CATEGORY = 3

def query_request(qtype: QueryType, id: int = -1) -> Response:
    if qtype == QueryType.PROBLEM:
        req = requests.get(f"https://acmicpc.net/problem/{id}")
    elif qtype == QueryType.PROBLEM_LIST:
        req = requests.get(f"https://acmicpc.net/step/{id}")
    elif qtype == QueryType.PROBLEM_CATEGORY:
        req = requests.get(f"https://acmicpc.net/step")
    
    return req

def print_usage():
    print("Usage: baekjoon (-c (id) | -l (id) | -p <id>) (-s <file path>)")

def print_problem_lists(id: int):
    pass

def print_problem_categories(id: int):
    req = query_request(QueryType.PROBLEM_CATEGORY, id)
    if req.status_code == 404:
        print("no such problem category with given id")
        return
    
    parser = ProblemCategoryParser()
    parser.feed(req.text)
    categories = parser.get_all_problem_category()

    for category in categories:
        print(f"{category.id} {category.title} - (0/{category.total_count})")

def print_problem_details(id: int):
    req = query_request(QueryType.PROBLEM, id)
    if req.status_code == 404:
        print("no such problem with given id")
        return
    
    parser = ProblemParser()
    parser.feed(req.text)
    detail = parser.get_problem_details()

    template = Template("""
        $id ($title)
        - $tlimit, $mem_limit 내로 해결해야 함
        - 현재 $submits 번 제출되었고, 그 중 $accepted_submits 개가 정답 처리됨
        
        문제:
         $desc

        입력:
         $input_desc

        출력:
         $output_desc
    """).substitute(
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

if __name__ == "__main__":
    if len(sys.argv)-1 == 0:
        print(f"Baekjoon TUI {TUI_VERSION}")
        print_usage()
        sys.exit()

    parse_commands(sys.argv)