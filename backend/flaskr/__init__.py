from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * CATEGORIES_PER_PAGE
    end = start + CATEGORIES_PER_PAGE

    categories = [category.format() for category in selection]
    current_categories = categories[start:end]

    return current_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return 'Hi'

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in selection}

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(Category.query.all())
        })

    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in categories}
        current_category = [question['category'] for question in current_questions]

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories,
            'current_category': current_category
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            return abort(404)
        try:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(500)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                current_category = [question.category for question in selection]
                current_questions = [question.format() for question in selection]

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                    'current_category': current_category
                })
            else:
                question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty,
                                    category=new_category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except:
            abort(500)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
        current_question = paginate_questions(request, selection)

        if len(current_question) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': len(selection)
        })

    @app.route('/quizzes', methods=['POST'])
    def retrieve_questions_for_quiz():
        body = request.get_json()
        questions_list = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        try:
            if quiz_category:
                if quiz_category['id'] == 0:
                    selection = Question.query.all()
                else:
                    selection = Question.query.filter(Question.category == quiz_category['id']).all()

            current_question = [question.format() for question in selection if question.id not in questions_list]

            if len(current_question) == 0:
                return jsonify({
                    'question': False
                })

            current_question = random.choice(current_question)
            return jsonify({
                'success': True,
                'question': current_question,
            })
        except:
            abort(500)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        })

    return app
