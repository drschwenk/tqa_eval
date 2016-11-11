from .common_utils import DataSetCommonTools
from collections import defaultdict
import random


class SimpleModels(DataSetCommonTools):
    def __init__(self, data_file):
        super(SimpleModels, self).__init__(data_file)
        self.predictions = defaultdict(list)

    def get_questions(self):
        if not self.dataset:
            self.load_dataset()
        all_questions = {}
        question_types = ['nonDiagramQuestions', 'diagramQuestions']
        for q_type in question_types:
            type_questions = [list(self.dict_key_extract(q_type, lesson)) for lesson in self.dataset]
            nd_questions = {}
            for lesson in type_questions:
                for lesson_questions in lesson:
                    for question_id, question in lesson_questions.items():
                        nd_questions[question_id] = question
            all_questions[q_type] = nd_questions
        filtered_questions = self.select_nd_mc_questions(all_questions)
        return filtered_questions



    def answer_question(self, question):
        return None

    def make_predictions(self):
        answers = {}
        if not self.dataset:
            self.load_dataset()
        all_questions = self.get_questions()
        for question_type, questions in all_questions.items():
            for qid, quest in questions.items():
                answers[qid] = self.answer_question(quest)
        return answers


class Guesser(SimpleModels):

    def answer_question(self, question):
        return random.choice(list(question['answerChoices'].keys()))


class Cheater(SimpleModels):

    def answer_question(self, question):
        return question['correctAnswer']['processedText']


