import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who am I?',
            'answer': 'Ibrahim',
            'difficulty': 5,
            'category': 1,
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_retrieve_questions(self):
        res = self.client().get('/questions?page=2')

        data = json.loads(res.data)
        self.assertEqual(len(data['questions']), 1)
        self.assertTrue(data['categories'])
        self.assertEqual(res.status_code, 200)

    def test_retrieve_questions_failed(self):
        res = self.client().get('/questions?page=100')
        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        # make sure there is a question with this id in the db, otherwise the test will fail.
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 20)

    def test_delete_question_failed(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertTrue(len(data['categories']))
        self.assertEqual(res.status_code, 200)

    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertEqual(len(data['categories']), 6)

    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 1)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_retrieve_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(len(data['questions']), 4)

    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/10/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search(self):
        res = self.client().post('/questions', json={'searchTerm': "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(type(data['total_questions']), int)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])

    def test_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions": [15, 16, 17],
                                                   "quiz_category": {'id': 1, 'type': 'Science'}})
        data = json.loads(res.data)

        self.assertTrue(data['question'])

    def test_quizzes_wrong_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [15, 16, 17],
                                                   "quiz_category": {'id': 9, 'type': 'Science'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()