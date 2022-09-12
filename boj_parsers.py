import requests
from dataclasses import dataclass
from dataclasses import field
from html.parser import HTMLParser

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
    time_limit: str = ''
    memory_limit: str = ''
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
    current_problem: Problem = Problem(ProblemPreview())
    is_parsing_table: bool = False
    table_index: int = 0
    parsing_id: str

    def handle_starttag(self, tag, attrs):
        '''
            HEAD
                <meta name="problem-id" content="(problem id)">
            BODY
                <span id="problem_title"> (title) </span>
                <div id="problem_description"> (desc) </div>
                <div id="problem_input"> (input desc) </div>
                <div id="problem_output"> (output desc) </div>
                <div id="problem_limit"> (limit desc) </div>
                <pre id="sample-input-[N]> (input testcase) </pre>
                <pre id="sample-output-[N]> (output testcase) </pre>
                <div id="problem_hint> (hint desc) </div>
            TBODY
                0           1           2.       3.                4.         5.
                time limit  mem. limit  submits  accepted submits  (unused)   (unused)
        '''
        if tag == "tbody":
            self.is_parsing_table = True
        if tag == "tr":
            self.table_index = 0
        if len(attrs) > 0 and attrs[0][0] == "id":
            self.parsing_id = attrs[0][1]

        if tag == "meta" and attrs[0][1] == "problem-id":
            self.current_problem.preview.id = int(attrs[1][1])
    
    def handle_data(self, data):
        if self.is_parsing_table:
            if self.table_index == 0:
                self.current_problem.time_limit = data.rstrip()
            elif self.table_index == 1:
                self.current_problem.memory_limit = data.rstrip()
            elif self.table_index == 2:
                self.current_problem.preview.submits = int(data)
            elif self.table_index == 3:
                self.current_problem.preview.accepted_submits = int(data)

        if hasattr(self, "parsing_id"):
            if self.parsing_id == "problem_title":
                self.current_problem.preview.title = data
            elif self.parsing_id == "problem_description":
                self.current_problem.description += data.lstrip()
            elif self.parsing_id == "problem_input":
                self.current_problem.input_desc += data.lstrip()
            elif self.parsing_id == "problem_output":
                self.current_problem.output_desc += data.lstrip()

        # FIXME: testcases and hints will be added soon

    def handle_endtag(self, tag):
        if (tag == "div" or tag == "pre" or tag == "span") and hasattr(self, "parsing_id"):
            del self.parsing_id
        if tag == "tbody":
            self.is_parsing_table = False
        if tag == "td" and self.is_parsing_table:
            self.table_index += 1

    def get_problem_details(self) -> Problem:
        return self.current_problem