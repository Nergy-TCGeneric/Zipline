#!/usr/bin/env python
"""
    Zipline
    For who even don't want to open gui browsers just to do tedious works
"""

import json
import math
import os
import sys
import argparse

from pathlib import Path
from string import Template
from zipline_component import *

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
    extract_username,
)

PUSHER_TOKEN = "a2cb611847131e062b32"
PADDING = 8


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
        raise ContentNotFound(wtype)
    if wtype == Webpage.SUBMIT and is_not_logged_in(req.text):
        raise NotLoggedIn

    return req


def is_not_logged_in(html: str) -> bool:
    username = extract_username(html)
    # https://peps.python.org/pep-0008/#programming-recommendations - Empty strings are falsy.
    return username


def print_problem_lists(id: int):
    try:
        req = get_webpage_of(Webpage.PROBLEM_LIST, id)
        previews = extract_all_problem_previews(req.text)

        for i in range(0, len(previews)):
            print(
                f"{i+1} {previews[i].title}({previews[i].id}) - {previews[i].accepted_submits}/{previews[i].submits}"
            )
    except Exception as e:
        raise e


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
    except Exception as e:
        raise e


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
    except Exception as e:
        raise e


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
    except Exception as e:
        raise e


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
        raise CandidateNotFound(file_path.suffix)


def prompt_user_select_languages(candidates: list[Language]) -> Language:
    while True:
        print("이용 가능한 언어 중 하나를 선택해주세요. 언어를 선택하시려면 괄호 안 숫자를 입력해주세요.")
        for c in candidates:
            print(f"{c.name} ({c.value}),", end=" ")
        print()

        selection = input("> ")
        if not selection.isdecimal():
            continue

        i = int(selection)
        for c in candidates:
            if c.value == i:
                return c


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
    candidates = []

    for l in Language:
        if ext == l.get_file_extension():
            candidates.append(l)

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


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--category", type=int, metavar="<CATEGORY ID>")
    parser.add_argument("-l", "--list", type=int, metavar="<LIST ID>")
    parser.add_argument("-p", "--problem", type=int, metavar="<PROBLEM ID>")
    parser.add_argument(
        "-s", "--submit", nargs=2, metavar=("<PROBLEM ID>", "<FILE PATH>")
    )

    return parser


def execute_command(args: argparse.Namespace):
    try:
        if args.category != None:
            print_problem_categories(args.category)
        elif args.list != None:
            print_problem_lists(args.list)
        elif args.problem != None:
            print_problem_details(args.problem)
        elif args.submit != None:
            postform = prepare_post_form(
                id=int(args.submit[0]), filename=args.submit[1]
            )
            submit_id = submit_solution(postform)
            show_judge_progress(submit_id)
    except KeyboardInterrupt:
        print("사용자가 조기에 프로그램을 종료했습니다.")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    parser = create_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    parsed = parser.parse_args(sys.argv[1:])
    execute_command(parsed)
