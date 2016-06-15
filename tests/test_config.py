from flask.ext.testing import TestCase
from flask import url_for
from manage import db, app
from config import config
import json
import base64


class BaseTestCase(TestCase):
    """A base test case for flask-tracking."""

    def create_app(self):
        """method for setting up config variables for the app"""
        app.config.from_object(config['testing'])
        return app

    def setUp(self):
        """setUp method"""
        self.app = self.create_app().test_client()
        db.create_all()
        resp_register = self.client.post(url_for('register'),
                                         data=json.dumps({'username':'Test',
                                                       'password':'1234'}),
                                         content_type="application/json")
        # print resp_register.json.get('id')
        response = self.client.post(url_for(
            'login'), data=json.dumps({'username':'Test',
                                                       'password':'1234'}),
                                         content_type="application/json")
        token = response.json
        self.token =  {'Authorization': 'token ' + token['Token']}

        self.bl_name = 'Bucketlist 1'

        new_bucketlist = self.client.post(url_for('bucketlists'),
            data=json.dumps({'list_name': self.bl_name,
              'created_by': resp_register.json.get('id')}),
            headers=self.token,
            content_type="application/json")


    def tearDown(self):
        """Clearing all settings"""
        db.session.remove()
        db.drop_all()

    def request(self, method, url, auth=None, **kwargs):
        """method to use to represent Authorization means for the tests"""
        return self.app.open(url, method=method, **kwargs)

    def test_index_route(self):
        """Test /api/v1.0/."""
        result = self.app.get('/api/v1.0/')
        result = json.loads(result.data)
        self.assertEqual(result, {'message': "Welcome to my bucketlist API."
                                  "" + " Send a POST request to /auth/register "
                                  "" + "with your login details "
                                  "" + "to get started."})
