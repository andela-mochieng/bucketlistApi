from flask.ext.testing import TestCase
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

    def tearDown(self):
        """Clearing all settings"""
        db.session.remove()
        db.drop_all()

    def request(self, method, url, auth=None, **kwargs):
        """method to use to represent Authorization means for the tests"""

        headers = kwargs.get('headers', {})
        print('hearder')
        print(headers)
        if auth:
            headers['Authorization'] = 'token ' + \
                base64.b64encode(auth[0] + ':' + auth[1])

        kwargs['headers'] = headers

        return self.app.open(url, method=method, **kwargs)

    def test_index_route(self):
        """Test /api/v1.0/."""
        result = self.app.get('/api/v1.0/')
        result = json.loads(result.data)
        self.assertEqual(result, {'message': "Welcome to my bucketlist API."
                                  "" + " Send a POST request to /auth/register "
                                  "" + "with your login details "
                                  "" + "to get started."})
