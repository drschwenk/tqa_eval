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
        total_answered_counts, overall_expected_score = self.validate_answer_format(predicted_answers)
        questions_by_type = self.build_question_lookup(by_type=True)
        questions_by_subtype = self.build_questions_by_subtype(questions_by_type['nonDiagramQuestions'])
        self.print_results(self.tabulate_results_by_type(questions_by_type, predicted_answers, overall_expected_score, total_answered_counts))
        print('Non-Diagram Question Type Breakdown')
        self.print_results(self.tabulate_results_by_type(questions_by_subtype, predicted_answers, overall_expected_score))
        return

    def tabulate_results_by_type(self, questions_by_type, predicted_answers, overall_expected_score, total_answered_counts=0,):
        results = []
        expected_totals = {}
        expected_by_chance = {}
        for question_type, questions in questions_by_type.items():
            expected_totals[question_type] = len(questions)
            expected_by_chance[question_type] = self.expected_score_by_chance(questions.values())
            for q_id, answer in predicted_answers.items():
                if q_id in questions.keys():
                    if self.answered_correctly(questions, q_id, answer):
                        results.append(question_type)
        correct_by_type = Counter(results)
        correct_by_type['overall'] = sum(correct_by_type.values())
        accuracies = self.compute_accuracies(correct_by_type, questions_by_type)
        expected_totals['overall'] = sum(expected_totals.values())
        expected_by_chance['overall'] = overall_expected_score
        results_to_tabulate = {
            'accuracy': accuracies,
            'total correct': correct_by_type,
            'number of questions expected': expected_totals,
            'baseline accuracy (random guesses)': expected_by_chance
        }
        if total_answered_counts:
            total_answered_counts['overall'] = sum(total_answered_counts.values())
            results_to_tabulate['number of questions answered'] = total_answered_counts
        return results_to_tabulate

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

    def expected_score_by_chance(self, q_series):
        total_q_n = len(q_series)
        ac_lengths_inv = []
        for quest in q_series:
            ac_lengths_inv.append(1 / len(quest['answerChoices']))
        expected_score = sum(ac_lengths_inv) / total_q_n
        return expected_score

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
        overall_expected_score = self.expected_score_by_chance(all_dataset_questions.values())
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
        return answered_questions_total, overall_expected_score

    def build_questions_by_subtype(self, nd_questions):
        subtypes = ["True or False", "Multiple Choice", "Matching"]
        questions_by_subtype = defaultdict(dict)
        for sub_type in subtypes:
            questions_by_subtype[sub_type] = {qid: question for qid, question in nd_questions.items()
                                              if question['questionSubType'] == sub_type}
        return questions_by_subtype

    def print_results(self, results):
        build_results = defaultdict(list)
        headers = ['question type'] + list(sorted(results.keys()))
        for result_type, results in sorted(results.items()):
            for q_type, result in sorted(results.items()):
                build_results[q_type].extend(["{0:.3f}".format(result)])
        display_results = [[k] + v for k, v in sorted(build_results.items())]
        print(tabulate(display_results, headers, tablefmt="fancy_grid"))

