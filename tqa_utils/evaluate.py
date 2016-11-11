from __future__ import division
import pandas as pd
import numpy as np
import json
from collections import defaultdict
from collections import Counter
import string
from tabulate import tabulate
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
        total_answered_counts = self.validate_answer_format(predicted_answers)
        results = []
        questions_by_type = self.build_question_lookup(by_type=True)
        expected_totals = {}
        for question_type, questions in questions_by_type.items():
            expected_totals[question_type] = len(questions)
            for q_id, answer in predicted_answers.items():
                if q_id in questions.keys():
                    if self.answered_correctly(questions, q_id, answer):
                        results.append(question_type)
        correct_by_type = Counter(results)
        correct_by_type['overall'] = sum(correct_by_type.values())
        accuracies = self.compute_accuracies(correct_by_type, questions_by_type)
        total_answered_counts['overall'] = sum(total_answered_counts.values())
        expected_totals['overall'] = sum(expected_totals.values())
        results_to_tabulate = {
            'accuracy': accuracies,
            'total correct': correct_by_type,
            'number of questions expected': expected_totals,
            'number of questions answered': total_answered_counts
        }
        self.print_results(results_to_tabulate)
        return accuracies

    def compute_accuracies(self, correct_by_type, questions_by_type):
        accuracy_by_type = {}
        for q_type, number_correct in correct_by_type.items():
            if q_type != 'overall':
                accuracy_by_type[q_type] = number_correct / len(questions_by_type[q_type])
            else:
                accuracy_by_type[q_type] = number_correct / sum([len(v) for v in questions_by_type.values()])
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
        all_dataset_questions = self.build_question_lookup()
        questions_missing = set(all_dataset_questions.keys()).difference(set(predicted_answers.keys()))
        if questions_missing:
            print('***Warning***')
            print('unanswered questions detected')
            print('recording missing files in missing_qids.txt')
            with open('missing_qids.txt', 'w') as f:
                f.write("\n".join(questions_missing))
        if not errors and not questions_missing:
            print('All validation test pass')
        elif not questions_missing:
            print('errors found ')
            for qid, error in errors.items():
                print(qid, ' ', error)

        answered_questions_total = {
            'diagramQuestions': len([qid for qid in predicted_answers if qid[0] == 'D']),
            'nonDiagramQuestions': len([qid for qid in predicted_answers if qid[0] == 'N'])
        }
        return answered_questions_total

    def print_results(self, results):
        build_results = defaultdict(list)
        headers = ['question type'] + list(sorted(results.keys()))
        for result_type, results in sorted(results.items()):
            for q_type, result in sorted(results.items()):
                build_results[q_type].extend(["{0:.2f}".format(result)])
        display_results = [[k] + v for k, v in sorted(build_results.items())]
        print(tabulate(display_results, headers, tablefmt="fancy_grid"))