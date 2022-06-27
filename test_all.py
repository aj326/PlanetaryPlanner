import json
from unittest import TestCase

import pytz
from astral import LocationInfo
from flask_sqlalchemy import SQLAlchemy

from app import app
from models import setup_db
from planetaryhours import check_location


class PlanetaryHourTest(TestCase):
    def test_check_location_lat1(self):
        with self.assertRaises(ValueError):
            check_location("test1", "T", "Asia/Riyadh", -97, 55)

    def test_check_location_long(self):
        with self.assertRaises(ValueError):
            check_location("test1", "T", "Asia/Riyadh", -90, -555)

    def test_check_location_tz(self):
        with self.assertRaises(pytz.UnknownTimeZoneError):
            check_location("test1", "T", "Asia/Riyadhhhhhhh", -90, -55)

    def test_check_location(self):
        self.assertIsInstance(check_location("test1", "T", "Asia/Riyadh", -90, -55), LocationInfo)


class APITestCase(TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_name = "test_planetary_planner"
        self.database_path = "postgresql://{}/{}".format('postgres:abc@localhost:5432', self.database_name)
        self.admin_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkxPeGtOeXViVk42TXhDRFBYcjRxUyJ9.eyJpc3MiOiJodHRwczovL3BsYS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJhZTkxY2E1NjM5ZjhkNGFkMjFjOWIxIiwiYXVkIjpbInBsYW5ldGFyeXBsYW5uZXIvYXBpIiwiaHR0cHM6Ly9wbGEudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY1NjI5MDI2OSwiZXhwIjoxNjU2Mzc2NjY5LCJhenAiOiI4NmRaVHZsQkdESjRNRW9vNVRkV1ZrbU9ueUFiTFRRRyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZXZlbnQiLCJkZWxldGU6aW5mbyIsImRlbGV0ZTp1c2VyIiwicGF0Y2g6ZXZlbnQiLCJwYXRjaDppbmZvIiwicGF0Y2g6bG9jYXRpb24iLCJwb3N0OmV2ZW50IiwicG9zdDppbmZvIiwicG9zdDpsb2NhdGlvbiIsInJlYWQ6bG9jYXRpb24iLCJyZWFkOnBsYW5ldGFyeWhvdXJzIiwicmVhZDpwbGFubmVyIiwicmVhZDp1c2VycyIsInRlc3Q6dGVzdCJdfQ.JqAqId4Nc6hHvne28ZCaiZL7dzjk86_HqBjMKIcIAHi3bRkkyEzcIfeFRMnAVROtCasW4p5ilk4Plw3t04gSMmh-W5tgY-xLeHHMeAj15abVEDE23tAM25hoPGU_ieZ0HhibGzSgdFHvx-BdpB52yVwNdBBNP2TiELnaHxlWCDvqA_cnlpuh5hGz4Og-aNkfoR7w6hmVahNfqZPNI7x5y_COn1Z2R3jzLtUSxRpzsPo8q_I-jYCPn8PwBKAKC0TJKPf2OUCoBnPodELIkBWvgUO_SPA-zMcLIu9Tepl1fEL8wLmiP_N2XCRKB-VzHc3Z-pUepzguWTCA98rI8KlATA'
        self.client_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkxPeGtOeXViVk42TXhDRFBYcjRxUyJ9.eyJpc3MiOiJodHRwczovL3BsYS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJiMGY3OTFmMzNmNmQ5NzQ2MDc1MDZjIiwiYXVkIjpbInBsYW5ldGFyeXBsYW5uZXIvYXBpIiwiaHR0cHM6Ly9wbGEudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY1NjI5NDIwMCwiZXhwIjoxNjU2MzgwNjAwLCJhenAiOiI4NmRaVHZsQkdESjRNRW9vNVRkV1ZrbU9ueUFiTFRRRyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZXZlbnQiLCJwYXRjaDpldmVudCIsInBhdGNoOmxvY2F0aW9uIiwicG9zdDpldmVudCIsInBvc3Q6bG9jYXRpb24iLCJyZWFkOmxvY2F0aW9uIiwicmVhZDpwbGFuZXRhcnlob3VycyIsInJlYWQ6cGxhbm5lciJdfQ.gCYZysDEv2c3wC6Av114VhgX5CnC-kdZHss9AxDY2RXagobZqyfpuVgWjG7SvFU3gW0SGBrakHcRoTkwaPg0fHWxdJd65B1lQPcPraiDo7_R0ZTt2fIe7JhbxTi3AfKH4XQrtsOad7cSzQ7-t0fydnDfwxkzOat-3gtRGDfWz7doDxGwuBJ3KGqd0HmKQgvyvHJmhqmoI3PGTgx_udkn-wpWgPZNlrgyOeiQI4sTuSNuMC383w286GrbUNYf-z8PVuZ7OAltSZyqU-tzeYi5o9EakheVsgE_8rSSGJphJWaMwpllf5l-8D1SCkmtICEfklZ2hm-5BNhh4DC-y7Q0WQ'
        setup_db(self.app, self.database_path)

        self.new_location = {"city": "Berlin",
                             "region": "MY ASS",
                             "timezone": "Europe/Berlin",
                             "latitude": 52.520008,
                             "longitude": 13.404954}

        self.new_bad_event = {"date": "22/22/22",
                              "hour": 22,
                              }
        self.new_good_event = {"date": "2/22/22",
                               "hour": 22,
                               }

        self.new_patch_event = {"date": "2/22/22",
                                "hour": 23,
                                }
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

    # Admin
    # get_users DONE
    # get_events DONE,DONE
    # get_planetary_hours DONE,DONE
    # get_location DONE,DONE
    # store_location DONE,DONE
    # post_event DONE,DONE
    # patch_event DONE, DONE
    # delete_user DONE,DONE
    # delete_event DONE, DONE

    def test_admin_get_users(self):
        res = self.client().get("/users", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_admin_get_locations_success(self):
        res = self.client().get("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["location"])

    def test_admin_get_locations_fail(self):
        res = self.client().get("/users/777/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_admin_get_events_success(self):
        res = self.client().get("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["user"])

    def test_admin_get_events_fail(self):
        res = self.client().get("/users/2222222/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_admin_get_planetary_hours_success(self):
        res = self.client().get("/users/22/planetaryhours", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["planetary_hours"])

    def test_admin_get_planetary_hours_fail(self):
        res = self.client().get("/users/777/planetaryhours", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_admin_store_location_success(self):
        res = self.client().post("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_location)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["location"])

    # TODO write more test cases ... in the future ;)
    def test_admin_store_location_fail_conflict(self):
        res = self.client().post("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_location)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 409)
        self.assertFalse(data["success"])

    def test_admin_post_event_success(self):
        res = self.client().post("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_good_event)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["event"])

    def test_admin_post_event_fail(self):
        res = self.client().post("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_bad_event)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])

    def test_admin_patch_event_success(self):
        res = self.client().patch("/events/18", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_patch_event)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["event"])

    def test_admin_patch_event_fail(self):
        res = self.client().patch("/events/1600", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)}, json=self.new_patch_event)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

        # TODO (For reviewer, change event id)

    def test_admin_delete_event_success(self):
        res = self.client().delete("/events/19", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_admin_delete_event_fail(self):
        res = self.client().delete("/events/1600", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

        # TODO (For reviewer, change user id)

    def test_admin_delete_user_success(self):
        res = self.client().delete("/users/24", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_admin_delete_user_fail(self):
        res = self.client().delete("/users/1600", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.admin_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

    # Client
    # get_users DONE
    # get_events DONE,DONE
    # get_planetary_hours DONE,DONE
    # get_location DONE,DONE
    # store_location DONE,DONE
    # post_event DONE,DONE
    # patch_event DONE, DONE
    # delete_user DONE
    # delete_event DONE, DONE

    def test_client_get_users(self):
        res = self.client().get("/users", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(data["success"])

    def test_client_get_locations_success(self):
        res = self.client().get("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["location"])

    def test_client_get_locations_fail(self):
        res = self.client().get("/users/777/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_client_get_events_success(self):
        res = self.client().get("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["user"])

    def test_client_get_events_fail(self):
        res = self.client().get("/users/2222222/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_client_get_planetary_hours_success(self):
        res = self.client().get("/users/22/planetaryhours", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["planetary_hours"])

    def test_client_get_planetary_hours_fail(self):
        res = self.client().get("/users/777/planetaryhours", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertTrue(data["message"])

    def test_client_store_location_success(self):
        res = self.client().post("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_location)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["location"])

    # TODO write more test cases ... in the future ;)
    def test_client_store_location_fail_conflict(self):
        res = self.client().post("/users/22/location", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_location)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 409)
        self.assertFalse(data["success"])

    def test_client_post_event_success(self):
        res = self.client().post("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_good_event)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["event"])

    def test_client_post_event_fail(self):
        res = self.client().post("/users/22/events", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_bad_event)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])

    def test_client_patch_event_success(self):
        res = self.client().patch("/events/20", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_patch_event)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["event"])

    def test_client_patch_event_fail(self):
        res = self.client().patch("/events/1600", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)}, json=self.new_patch_event)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

        # TODO (For reviewer, change event id)

    def test_client_delete_event_success(self):
        res = self.client().delete("/events/20", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_client_delete_event_fail(self):
        res = self.client().delete("/events/1600", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

        # TODO (For reviewer, change user id)

    def test_client_delete_user_success_auth_error(self):
        res = self.client().delete("/users/24", follow_redirects=True, headers={
            'Authorization': 'Bearer {}'.format(self.client_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
