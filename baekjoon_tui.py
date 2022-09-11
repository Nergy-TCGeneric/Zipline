import requests
from dataclasses import dataclass
from dataclasses import field
from html.parser import HTMLParser

'''
    Baekjoon TUI
    For who don't want to open gui browsers for some reason
'''

@dataclass
class ProblemCategory:
    id: int = -1
    title: str = ''
    description: str = ''
    total_count: int = -1
    solved_count: int = -1

@dataclass
class ProblemPreview:
    id: int = -1
    title: str = ''
    labels: str = ''
    accepted_submits: int = -1
    submits: int = -1

@dataclass
class Problem:
    preview: ProblemPreview
    time_limit: int = -1
    memory_limit: int = -1 # in kbyte
    description: str = ''
    input_desc: str = ''
    output_desc: str = ''

class ProblemCategoryParser(HTMLParser):
    categories: list[ProblemCategory] = []
    current_category: ProblemCategory
    is_parsing_table: bool = False
    table_index: int = 0

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.is_parsing_table = True
        if tag == "tr" and self.is_parsing_table:
            # Baekjoon's HTML is partially broken(no 'tr' endtag), so everything must be packaged at here
            if hasattr(self, "current_category"):
                self.categories.append(self.current_category)
            self.current_category = ProblemCategory()
            self.table_index = 0

    def handle_data(self, data):
        '''
            0    1      2             3         4           5
            id   title  description   (unused)  total_cnt   solved
        '''
        if not self.is_parsing_table:
            return

        if self.table_index == 0:
            self.current_category.id = int(data.rstrip())
        elif self.table_index == 1:
            self.current_category.title = data
        elif self.table_index == 2:
            self.current_category.description = data
        elif self.table_index == 3:
            return
        elif self.table_index == 4:
            self.current_category.total_count = int(data.rstrip())
        elif self.table_index == 5:
            self.current_category.solved_count = int(data.rstrip())
        else:
            raise ValueError('Tried to parse table over boundary')

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.is_parsing_table = False
        if tag == "td" and self.is_parsing_table:
            self.table_index += 1

    def get_Nth_problem_category(self, N: int) -> ProblemCategory:
        return self.categories[N]

    def get_all_problem_category(self) -> list[ProblemCategory]:
        return self.categories

class ProblemListParser(HTMLParser):
    problems: list[ProblemPreview] = []
    current_preview: ProblemPreview
    is_parsing_table: bool = False
    is_parsing_description: bool = False
    table_index: int = 0

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.is_parsing_table = True
        if tag == "tr" and self.is_parsing_table:
            self.current_preview = ProblemPreview()
            self.table_index = 0

    def handle_data(self, data):
        '''
            0          1           2       3                4          5        6
            (unused)   problem_id  title   label(optional)  accepted   submits  ratio
        '''
        if not self.is_parsing_table:
            return
        
        # FIXME: Not this time. Will be implemented soon
        if self.is_parsing_description:
            return
        
        if self.table_index == 1:
            self.current_preview.id = int(data.rstrip())
        elif self.table_index == 2:
            self.current_preview.title = data
        elif self.table_index == 3:
            self.current_preview.labels = data
        elif self.table_index == 4:
            self.current_preview.accepted_submits = int(data.rstrip())
        elif self.table_index == 5:
            self.current_preview.submits = int(data.rstrip())
        elif self.table_index > 6:
            raise ValueError('Tried to parse table over boundary')

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.is_parsing_table = False
        if tag == "td" and self.is_parsing_table:
            self.table_index += 1
        # Oddly, all end tags are intact in problem list page. oh, those inconsistencies..
        if tag == "tr":
            if not self.is_parsing_description:
                self.problems.append(self.current_preview)
            self.is_parsing_description = not self.is_parsing_description

    def get_Nth_problem_preview(self, N:int) -> ProblemPreview:
        return self.problems[N]
    
    def get_all_problem_previews(self) -> list[ProblemPreview]:
        return self.problems

class ProblemParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("start tag: ", tag)
    
    def handle_data(self, data):
        print("data: ", data)

    def handle_endtag(self, tag):
        print("end tag: ", tag)

baekjoon_req = requests.get("https://acmicpc.net/step")
parser = ProblemCategoryParser()
parser.feed(baekjoon_req.text)
# print(baekjoon_req.text)