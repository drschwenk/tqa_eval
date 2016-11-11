import os
import json
import jinja2
import argparse

j2env = jinja2.Environment()

default_page_html = """
<!DOCTYPE html>
<html>
  <head>
    <style type="text/css">
       .container {
            max-width: 800px;
          }
    </style>
  </head>
  <body style=max-width: 100px>
    <div class="container">
      <h1>Lesson: {{lesson}}</h1>
      <ul>
        {% for topic in topics %}
        <p>
        </p>
        <h3>{{topic.0}}</h3>
        <p>{{topic.1}}</p>
        {% endfor %}
      </ul>
    </div>
    <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
  </body>
</html>
"""

diagram_page_html = """
<!DOCTYPE html>
<html>
  <head>
    <style type="text/css">
       .container {
          }
    </style>
  </head>
  <body style=max-width: 100px>
    <div class="container">
      <h1>Lesson: {{lesson}}</h1>
      <ul>
        {% for topic in topics %}
        <p>
        </p>
        <p>{{topic}}</p>
        {% endfor %}
      </ul>
    </div>
    <script src="http://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
  </body>
</html>
"""


def make_lesson_data(lesson_json, rel_html_out_path=None):
    nested_text = []
    for topic, content in sorted(lesson_json['topics'].items(), key=lambda kv: kv[1]['globalID']):
        nested_text.append((content['topicName'], content['content']['text']))
        if content['content']['figures']:
            for figure in content['content']['figures']:
                image_link = '<img src="' + '../../' + figure['imagePath'] + '" width=500px>'
                image_caption = figure['caption']
                nested_text.append(('', image_link))
                nested_text.append(('', image_caption))
    
    for topic, content in lesson_json['adjunctTopics'].items():
        if topic == 'Vocabulary':
            nested_text.append((topic, ''))            
            for k, v in content.items():
                nested_text.append(('', k + ':  ' + v))
        else:
            nested_text.append((topic, content['content']['text']))
            if content['content']['figures']:
                for figure in content['content']['figures']:
                    image_link = '<img src="' + '../../' + figure['imagePath'] + '" width=500px>'
                    image_caption = figure['caption']
                    nested_text.append(('', image_link))
                    nested_text.append(('', image_caption))
    return nested_text



def make_lesson_wdq_data(lesson_json, rel_html_out_path, question_type='diagramQuestions'):
    nested_text = []
    for question in sorted(lesson_json['questions'][question_type].values(), key=lambda x: x['globalID']):
        image_link = '<img src="' + '../../' + question['imagePath'] + '" width=500px>'
        nested_text.append(image_link)
        nested_text.append(question['globalID'])
        being_asked = question['beingAsked']['processedText']
        nested_text.append(being_asked)
        for ac in sorted(question['answerChoices'].values(), key=lambda x: x['idStructural']):
            if ac['processedText'] == question['correctAnswer']['processedText']:
                nested_text.append('<font color="red"> ' + ' '.join([' ', ac['idStructural'], ac['processedText']]) + '</font>')
            else:
                nested_text.append(' '.join([' ', ac['idStructural'], ac['processedText']]))
        nested_text.append('')
    return nested_text


def make_lesson_wq_data(lesson_json, rel_html_out_path, question_type='diagramQuestions'):
    nested_text = []
    for question in sorted(lesson_json['questions'][question_type].values(), key=lambda x: x['globalID']):
        if question['questionType'] in ["Direct Answer"]:
            continue
        if question_type == 'diagramQuestion':
            image_link = '<img src="' + '../../' + question['imagePath'] + '" width=500px>'
            nested_text.append(image_link)
        nested_text.append(question['globalID'])
        being_asked = question['beingAsked']['processedText']
        nested_text.append(being_asked)
        for ac in sorted(question['answerChoices'].values(), key=lambda x: x['idStructural']):
            if 'correctAnswer' not in question.keys() or'processedText' not in question['correctAnswer'].keys():
                continue
            if question['correctAnswer']['processedText'] in [ac['processedText'], ac['idStructural'].replace('.', '').replace(')', '')]:
                nested_text.append('<font color="red"> ' + ' '.join([' ', ac['idStructural'], ac['processedText']]) + '</font>')
            else:
                nested_text.append(' '.join([' ', ac['idStructural'], ac['processedText']]))
        nested_text.append('')
    return nested_text


def make_lesson_diagram_description_data(lesson_json, rel_html_out_path):
    nested_text = []
    for description in sorted(list(lesson_json['instructionalDiagrams'].values()), key=lambda x: x['imagePath']):
        image_link = '<img src="' + '../../' + description['imagePath'] + '" width=500px>'
        nested_text.append(image_link)
        nested_text.append(description['imageName'])
        being_asked = description['processedText']
        nested_text.append(being_asked)
        nested_text.append('')
    return nested_text


def make_page_html(lesson_data, page_html):
    return j2env.from_string(page_html).render(lesson=lesson_data[0], topics=lesson_data[1])


def display_lesson_html(lesson_json, lesson, page_type=None, html_output_dir=None):
    if not page_type or page_type == 'lessons':
        lesson_data = (lesson, make_lesson_data(lesson_json, html_output_dir))
        page_html = default_page_html
    elif page_type == 'questions':
        lesson_data = (lesson, make_lesson_wq_data(lesson_json, html_output_dir, 'nonDiagramQuestions'))
        page_html = diagram_page_html        
    elif page_type == 'diagram_questions':
        lesson_data = (lesson, make_lesson_wdq_data(lesson_json, html_output_dir))
        page_html = diagram_page_html
    elif page_type == 'diagram_descriptions':
        lesson_data = (lesson, make_lesson_diagram_description_data(lesson_json, html_output_dir))
        page_html = diagram_page_html
    lesson_html = make_page_html(lesson_data, page_html)
    return lesson_html


def make_lesson_html(flexbook, lesson, page_html=default_page_html):
    lesson_json = flexbook[lesson]
    lesson_data = (lesson, make_lesson_data(lesson_json))
    lesson_html = make_page_html(lesson_data, page_html)
    return lesson_html


def render_html_from_dataset(path_to_data_json):
    with open(path_to_data_json, 'r') as f:
        ck12_combined_dataset = json.load(f)
    out_path = '../html_renders' 
    render_types = ['lessons', 'diagram_questions', 'diagram_descriptions', 'questions']
    for render in render_types:
        html_dir = os.path.join('html_renders', render)
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        for lesson in ck12_combined_dataset:
            if render == 'lessons':
                json_out_file = os.path.join(html_dir, lesson['lessonName'].replace(' ', '_') + '_' + lesson['globalID'] + '.json') 
                with open(json_out_file, 'w') as f:
                    json.dump(lesson, f, indent=4, sort_keys=True)
            elif render == 'questions':
                pass
            elif not lesson['questions']['diagramQuestions']:
                continue
            lesson_html = display_lesson_html(lesson, lesson['lessonName'], render, out_path)
            html_out_file = os.path.join(html_dir, lesson['lessonName'].replace(' ', '_') + '_' + lesson['globalID'] + '.html')
            with open(html_out_file, 'w') as f:
                f.write(lesson_html.encode('ascii', 'ignore').decode('utf-8'))
            

def main():
    parser = argparse.ArgumentParser(description='Generates HTML pages from the dataset for review')
    parser.add_argument('dataset', help='path to complete dataset', type=str)
    args = parser.parse_args()
    data_path = args.dataset
    render_html_from_dataset(data_path)
   

if __name__ == "__main__":
    main()
