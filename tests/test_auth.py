from flask import url_for
import json
from test_config import BaseTestCase
from app.models import User
from app.resources import auth, verify_password
from manage import db, app



class RegistrationTest(BaseTestCase):
    """Testing signup  and login of a user"""

    def test_user_registers_with_correct_info(self):
        """ Test that user can register"""
        response = self.client.post(url_for('register'),
                                    data=json.dumps(
                                        {'username': 'Margie', 'password': 'bucket'}),
                                    content_type='application/json')
        self.assertIn('User successfully created', response.data)
        self.assertEqual(response.status_code, 201)

    def test_if_registration_details_are_missing_user_is_not_registered(self):
        """ Test if registration details are missing user is not registered"""
        response = self.client.post(url_for('register'),
                                    data=json.dumps({'username': 'Magie'}),
                                    content_type='application/json')
        self.assertIn("Bad Request", response.data)
        self.assertEqual(response.status_code, 400)

    def test_an_existing_user_cant_signup_again(self):
        """ Test that users have unique details"""
        user = User(username='Margie', password='1234')
        db.session.add(user)
        db.session.commit()
        response = self.client.post(url_for('register'),
                                    data=json.dumps({'username': 'Margie', 'password': '1234'}), content_type='application/json')
        self.assertIn("Username already exists", response.data)
        self.assertEqual(response.status_code, 200)


    def test_users_can_not_sign_up_when_they_provide_no_info(self):
        """tests that creation of a user fails
        when no info is sent"""
        response = self.client.post(url_for('register'),
                                    data=json.dumps({'username': '', 'password': ''}), content_type='application/json')
        self.assertIn("Kindly enter your username and password", response.data)
        self.assertEqual(response.status_code, 200)
