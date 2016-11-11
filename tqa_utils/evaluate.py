from __future__ import division
import pandas as pd
import numpy as np
import json
from collections import defaultdict
from collections import Counter
import string
from .common_utils import DataSetCommonTools


class Evaluator(DataSetCommonTools):
    def __init__(self, data_json_file):
        super(Evaluator, self).__init__(data_json_file)
        self.dataset = None

    def evaluate_model(self, predicted_answers):

        if isinstance(predicted_answers, str):
            with open(predicted_answers, 'r') as f:
                predicted_answers = json.load(f)
        if not self.dataset:
            self.load_dataset()
        validation_errors = self.validate_answer_format(predicted_answers)
        if not validation_errors:
            print('All validation test pass')
        else:
            print('errors found ')
            for qid, error in validation_errors.items():
                print(qid, ' ', error)
        results = []
        questions_by_type = self.build_question_lookup(by_type=True)
        for question_type, questions in questions_by_type.items():
            for q_id, answer in predicted_answers.items():
                if q_id in questions.keys():
                    if self.answered_correctly(questions, q_id, answer):
                        results.append(question_type)
        correct_by_type = Counter(results)
        accuracies = self.compute_accuracies(correct_by_type, questions_by_type)
        print(accuracies)
        return accuracies

    def compute_accuracies(self, correct_by_type, questions_by_type):
        accuracy_by_type = {}
        for q_type, number_correct in correct_by_type.items():
            accuracy_by_type[q_type] = number_correct / len(questions_by_type[q_type])

        accuracy_by_type['overall_accuracy'] = sum(correct_by_type.values()) / sum([len(v) for v in questions_by_type.values()])
        return accuracy_by_type

    def answered_correctly(self, questions_for_type, q_id, answer):
        return answer == questions_for_type[q_id]['correctAnswer']['processedText']

    def validate_answer_format(self, predicted_answers):
        errors = defaultdict(list)
        for qid, answer in predicted_answers.items():
            id_prefix, id_number = qid.split('_')
            if id_prefix not in ['DQ', 'NDQ']:
                errors[qid].append('bad id prefix')
            if len(id_number) != 6:
                errors[qid].append('bad id number')
            if answer not in string.ascii_letters:
                errors[qid].append('answer not a letter index')
        return errors