from invoke import task
import tqa_utils.render_html as render_html
from tqa_utils.validate_and_split import DataSetIntegrityChecker
from tqa_utils.validate_and_split import TestTrainSplitter
from tqa_utils.evaluate import Evaluator


@task
def make_html(context, data_path='tqa_dataset.json'):
    render_html.render_html_from_dataset(data_path)


@task
def test_train_split(context):
    pass

@task 
def compute_accuracies(context, data_path='tqa_dataset.json', answer_path=''):
    model_evaluator = Evaluator(data_path)
    accuracies = model_evaluator.evaluate_model(answer_path)
    return accuracies
