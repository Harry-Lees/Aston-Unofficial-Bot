from flask import Blueprint, render_template
from app.extensions import database
from .models import Quiz, Variant, Question
from .forms import QuizForm, AnswerForm

blueprint = Blueprint('quiz_support', __name__, template_folder = 'templates', url_prefix = '/quiz_support')


@blueprint.route('/')
def index():
    quizzes = Quiz.query.all()
    return render_template('quiz_index.html', quizzes = quizzes)


@blueprint.route('/quiz/<quiz_name>')
def quiz(quiz_name: str):
    quiz = Quiz.query.filter_by(title = quiz_name).first_or_404()

    return render_template('quiz.html', quiz = quiz)


@blueprint.route('/upload', methods = ['GET', 'POST'])
def upload():
    quiz_form = QuizForm()
    answer_form = AnswerForm()


    if quiz_form.validate_on_submit():
        new_quiz = Quiz(title = quiz_form.title.data, type = quiz_form.quiz_type.data)
        database.session.add(new_quiz)

        for i in range(1, quiz_form.num_questions.data + 1):
            question = Question(question_id = i, quiz = new_quiz)
            database.session.add(question)

        database.session.commit()


    if answer_form.validate_on_submit():
        quiz = answer_form.quiz.data
        question = Question.query.filter_by(quiz = quiz, question_id = 1).first()

        new_variant = Variant(
            question = question,
            image_path = None,
            description = answer_form.description.data,
            transcript = answer_form.transcript.data,
            answer = answer_form.answer.data
        )

        database.session.add(new_variant)
        database.session.commit()

        print('answer form submitted')

    return render_template('upload.html', quiz_form = quiz_form, answer_form = answer_form)