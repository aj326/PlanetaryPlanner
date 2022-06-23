from unittest import TestCase

import pytz
from astral import LocationInfo
import os
import json
from flask_sqlalchemy import SQLAlchemy

from app import app
from models import setup_db, User, Location, Events

from planetaryhours import my_location


class PlanetaryHourTest(TestCase):
    def test_my_location_lat1(self):
        with self.assertRaises(ValueError):
            my_location("test1","T","Asia/Riyadh",-97,55)
    def test_my_location_long(self):
        with self.assertRaises(ValueError):
            my_location("test1","T","Asia/Riyadh",-90,-555)
    def test_my_location_tz(self):
        with self.assertRaises(pytz.UnknownTimeZoneError):
            my_location("test1","T","Asia/Riyadhhhhhhh",-90,-55)
    def test_my_location(self):
        self.assertIsInstance(my_location("test1","T","Asia/Riyadh",-90,-55),LocationInfo)





class APITestCase(TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_name = "test_planetary_planner"
        self.database_path = "postgresql://{}/{}".format('postgres:abc@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # self.new_question = {"question": "TEST What color is the sky?",
        #                      "answer": "TEST blue",
        #                      "difficulty": 1,
        #                      "category": 1}
        # self.new_bad_question = {"question": "TEST What color is the sky?",
        #                          "difficulty": 1,
        #                          "category": 1}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # GET, Questions
    # Endpoint: '/questions[?pages=num]', Method: GET
    def test_get_users(self):
        res = self.client().get("/users", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)
        # self.assertTrue(data["users"])
        # self.assertTrue(data["users"]["username"])
        # self.assertTrue(data["users"]["id"])

    # Endpoint: `/questions?page=num`, Method: GET
    def test_get_locations(self):
        res = self.client().get("/users/16/location", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["location"])
    def test_get_locations_404(self):
        res = self.client().get("/users/777/location", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_get_planetary_hours(self):
        res = self.client().get("/users/16/planetaryhours", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["planetary_hours"])

    def test_404_get_planetary_hours(self):
        res = self.client().get("/users/777/planetaryhours", follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    #
    # # GET, Categories:
    # # Endpoint: '/categories', Method: GET
    # def test_get_categories(self):
    #     res = self.client().get("/categories", follow_redirects=True)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["categories"])
    #
    # # Endpoint: '/categories/{id}', Method: GET
    # def test_get_category(self):
    #     res = self.client().get("/categories/5", follow_redirects=True)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data["success"], False)
    #
    # def test_get_questions_for_category(self):
    #     res = self.client().get("/categories/1/questions", follow_redirects=True)
    #     print(res.data)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(len(data["questions"]))
    #     self.assertTrue(data["totalQuestions"])
    #     self.assertTrue(data["currentCategory"])
    #
    # def test_get_questions_for_invalid_category(self):
    #     res = self.client().get("/categories/100000/questions", follow_redirects=True)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "Resource not found")
    #
    # # POST, Questions:
    # def test_post_new_question(self):
    #     res = self.client().post("/questions", follow_redirects=True, json=self.new_question)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["question"])
    #     self.assertTrue(data["answer"])
    #     self.assertTrue(data["difficulty"])
    #     self.assertTrue(data["category"])
    #
    # def test_422_post_new_question_not_allowed(self):
    #     res = self.client().post("/questions", follow_redirects=True, json=self.new_bad_question)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "Unprocessable Entity")
    #
    # def test_search_for_questions(self):
    #     res = self.client().post("/questions", follow_redirects=True, json={"searchTerm": "Title"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['success'])
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(data['totalQuestions'])
    #     self.assertIsNone(data['currentCategory'])
    #
    # def test_search_for_questions_returns_no_quetions(self):
    #     res = self.client().post("/questions", follow_redirects=True, json={"searchTerm": "Title0000000000000"})
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['success'])
    #     self.assertFalse(len(data['questions']))
    #     self.assertFalse(data['totalQuestions'])
    #     self.assertIsNone(data['currentCategory'])
    #
    # def test_quizz_with_cat(self):
    #     res = self.client().post("/quizzes", follow_redirects=True,
    #                              json={"previous_questions": [1, 2, 3], "quiz_category": {"id": 2}})
    #     data = json.loads(res.data)
    #     self.assertTrue(data['success'])
    #     self.assertTrue(data['question'])
    #
    # def test_quizz_without_cat(self):
    #     res = self.client().post("/quizzes", follow_redirects=True,
    #                              json={"previous_questions": [1, 2, 3], "quiz_category": {"id": 0}})
    #     data = json.loads(res.data)
    #     self.assertTrue(data['success'])
    #     self.assertTrue(data['question'])
    #
    # def test_delete_success(self):
    #     prev_res = self.client().get("/questions", follow_redirects=True)
    #     prev_total = (json.loads(prev_res.data))['totalQuestions']
    #     res = self.client().delete("/questions/16", follow_redirects=True)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['success'])
    #     self.assertEqual(data["totalQuestions"], prev_total - 1)
    #     self.assertTrue(len(data["questions"]))
    #     self.assertTrue(len(data["categories"]))
    #     self.assertIsNone(data["currentCategory"])
    #
    # def test_delete_fail(self):
    #     res = self.client().delete("/questions/1600", follow_redirects=True)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 404)
    #     self.assertFalse(data["success"])
    #     self.assertEqual(data["message"], "Resource not found")
    #

# Make the tests conveniently executable

