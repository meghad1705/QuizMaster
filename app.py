from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime
from firebase_admin import firestore
from firebase_config import db

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch all quizzes from Firestore (or mock db)
    quizzes = []
    try:
        docs = db.collection('quizzes').stream()
        for doc in docs:
            quiz_data = doc.to_dict()
            quiz_data['id'] = doc.id
            quizzes.append(quiz_data)
    except Exception as e:
        print(f"Error fetching quizzes: {e}")
    return render_template('index.html', quizzes=quizzes)

@app.route('/create', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        # Get individual quiz details
        title = request.form.get('title')
        description = request.form.get('description')
        timer = int(request.form.get('timer', 30))
        questions = json.loads(request.form.get('questions_json'))

        quiz_data = {
            'title': title,
            'description': description,
            'timer': timer,
            'questions': questions
        }

        # Store quiz in Firestore
        new_quiz_ref = db.collection('quizzes').add(quiz_data)
        
        return redirect(url_for('index'))
    return render_template('create_quiz.html')

@app.route('/take/<quiz_id>')
def take_quiz(quiz_id):
    # Fetch quiz data
    doc = db.collection('quizzes').document(quiz_id).get()
    if doc.exists:
        quiz = doc.to_dict()
        quiz['id'] = doc.id
        return render_template('take_quiz.html', quiz=quiz)
    return "Quiz not found", 404

@app.route('/submit/<quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    # Fetch the original quiz to evaluate
    doc = db.collection('quizzes').document(quiz_id).get()
    if not doc.exists:
        return "Quiz not found", 404
        
    quiz = doc.to_dict()
    user_answers = request.form.to_dict()
    user_name = user_answers.pop('userName', 'Anonymous')
    
    score = 0
    total_questions = len(quiz['questions'])
    results = []

    for idx, q in enumerate(quiz['questions']):
        correct_answer = q['answer'].strip().lower()
        user_answer = user_answers.get(f'question_{idx}', '').strip().lower()
        
        is_correct = (user_answer == correct_answer)
        if is_correct:
            score += 1
        
        results.append({
            'question': q['text'],
            'user_answer': user_answer,
            'correct_answer': q['answer'],
            'is_correct': is_correct
        })

    # Save the result to Firestore
    try:
        ts = firestore.SERVER_TIMESTAMP
    except:
        ts = datetime.now().isoformat()

    result_data = {
        'quiz_id': quiz_id,
        'user_name': user_name,
        'score': score,
        'total': total_questions,
        'timestamp': ts
    }
    
    db.collection('results').add(result_data)

    return render_template('result.html', 
                            quiz=quiz, 
                            score=score, 
                            total=total_questions, 
                            results=results, 
                            user_name=user_name)

@app.route('/leaderboard/<quiz_id>')
def leaderboard(quiz_id):
   # Fetch real-time leaderboard data
   results = []
   try:
       # For local mock mode, we manually filter
       all_results = db.collection('results').stream()
       for doc in all_results:
           data = doc.to_dict()
           if data.get('quiz_id') == quiz_id:
               results.append(data)
       
       # Sort results by score (descending)
       results.sort(key=lambda x: x.get('score', 0), reverse=True)
   except Exception as e:
       print(f"Error fetching leaderboard: {e}")

   # Sanitize for JSON (convert timestamps to strings)
   for res in results:
       if 'timestamp' in res and not isinstance(res['timestamp'], (str, int, float, bool, type(None))):
           res['timestamp'] = str(res['timestamp'])

   return jsonify(results[:10]) # Return top 10 as JSON

if __name__ == '__main__':
    app.run(debug=True)
