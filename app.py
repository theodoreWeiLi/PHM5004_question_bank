import json
import os
from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def load_questions():
    questions_file = os.environ.get('QUESTIONS_FILE', 'questions.json')
    with open(questions_file) as f:
        return json.load(f)

questions = load_questions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions', methods=['GET'])
def get_questions():
    if 'progress' not in session:
        session['progress'] = {
            'completed': [],
            'requeued': [],
            'correct': 0,
            'incorrect': 0
        }
    
    # Validate session indices in case question bank changed
    total_md = len(questions)
    session['progress']['requeued'] = [i for i in session['progress']['requeued'] if i < total_md]
    session['progress']['completed'] = [i for i in session['progress']['completed'] if i < total_md]
    session.modified = True

    requeued_questions = session['progress']['requeued']
    if requeued_questions:
        question_index = requeued_questions.pop(0)
        question = questions[question_index]
        question['index'] = question_index
        session.modified = True
        return jsonify(question)

    remaining_questions = [i for i, q in enumerate(questions) if i not in session['progress']['completed']]
    
    if not remaining_questions:
        return jsonify({'completed': True})

    question_index = random.choice(remaining_questions)
    question = questions[question_index]
    question['index'] = question_index
    return jsonify(question)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    question_index = data.get('question_index')
    selected_option = data.get('selected_option')

    if question_index is None or question_index >= len(questions) or question_index < 0:
        return jsonify({'error': 'Invalid question index'}), 400

    question = questions[question_index]
    correct_option = question['answer']

    if 'progress' not in session:
        # initialize if somehow missing
        session['progress'] = {
            'completed': [],
            'requeued': [],
            'correct': 0,
            'incorrect': 0
        }

    if selected_option == correct_option:
        session['progress']['completed'].append(question_index)
        session['progress']['correct'] = session['progress'].get('correct', 0) + 1
        session.modified = True
        return jsonify({'correct': True, 'analysis': question['analysis']})
    else:
        session['progress']['requeued'].append(question_index)
        session['progress']['incorrect'] = session['progress'].get('incorrect', 0) + 1
        session.modified = True
        return jsonify({'correct': False, 'analysis': question['analysis']})


@app.route('/stats', methods=['GET'])
def stats():
    # Ensure progress exists
    if 'progress' not in session:
        session['progress'] = {
            'completed': [],
            'requeued': [],
            'correct': 0,
            'incorrect': 0
        }

    total = len(questions)
    completed = len(session['progress'].get('completed', []))
    left = total - completed
    correct = session['progress'].get('correct', 0)
    incorrect = session['progress'].get('incorrect', 0)

    return jsonify({
        'total_questions': total,
        'questions_left': left,
        'correct_answers': correct,
        'incorrect_answers': incorrect
    })


@app.route('/restart', methods=['POST'])
def restart():
    # Reset progress for a new practice turn
    session['progress'] = {
        'completed': [],
        'requeued': [],
        'correct': 0,
        'incorrect': 0
    }
    session.modified = True
    return jsonify({'restarted': True})

@app.route("/hello")
def hello():
    return "Hello, world!"

if __name__ == '__main__':
    # Force reload if questions.json changed
    port = int(os.environ.get('PORT', '5001'))
    app.run(host='127.0.0.1', port=port, debug=True)
