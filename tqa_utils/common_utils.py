import os
import json


class DataSetCommonTools(object):

    def __init__(self, data_file):
        self.data_json_file = data_file
        self.dataset = None

    def dict_key_extract(self, key, var):
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.dict_key_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.dict_key_extract(key, d):
                            yield result

    def load_dataset(self):
        with open(self.data_json_file, 'r') as f:
            self.dataset = json.load(f)

    def build_question_lookup(self, by_type=False):
        self.load_dataset()
        non_diagram_questions = [list(self.dict_key_extract('nonDiagramQuestions', lesson)) for lesson in self.dataset]
        diagram_questions = [list(self.dict_key_extract('diagramQuestions', lesson)) for lesson in self.dataset]

        nd_questions = {}
        for lesson in non_diagram_questions:
            for lesson_questions in lesson:
                for question_id, question in lesson_questions.items():
                    nd_questions[question_id] = question
        d_questions = {}
        for lesson in diagram_questions:
            for lesson_questions in lesson:
                for question_id, question in lesson_questions.items():
                    d_questions[question_id] = question
        diagrams_by_type = self.select_nd_mc_questions({'diagramQuestions': d_questions, 'nonDiagramQuestions': nd_questions})
        if by_type:
            return diagrams_by_type
        else:
            return {**diagrams_by_type['diagramQuestions'], **diagrams_by_type['nonDiagramQuestions']}

    def select_nd_mc_questions(self, all_questions):
        non_dqs = all_questions['nonDiagramQuestions']
        selected_questions = {qid: question for qid, question in non_dqs.items() if
                              question['questionType'] == 'Multiple Choice'}
        all_questions['nonDiagramQuestions'] = selected_questions
        return all_questions