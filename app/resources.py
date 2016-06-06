from collections import OrderedDict
from flask.ext.restful import Resource, marshal
from flask import g, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import BucketList, User, BucketListItem
from serializers import user_serializer, bucketlist_serializer, bucketlistitem_serializer

auth = HTTPBasicAuth()


class Home(Resource):
    """
    Handles requests to home route.
    Resource url:
        '/'
    Endpoint:
        'home'
    Requests Allowed:
        GET
    """

    def get(self):
        """
        Returns:
            A json welcome message
        """
        return jsonify({"message": "Welcome to my bucketlist API."
                        "" + " Send a POST request to /auth/register "
                        "" + "with your login details "
                        "" + "to get started."})


@auth.verify_password
def verify_password(token, password):
    """
    Verify a user's password.
    Args:
        token:
        password:
    retuns:
        True if the password is correct.
    """
    token = request.headers.get('GainAccess')
    if token is not None:
        user = User.verify_auth_token(token)
        if user:
            g.user = user
            return True
    return False


@auth.error_handler
def unauthorized():
    """Alert user that a token is invalid"""
    return make_response(jsonify({'error': 'Invalid Token', 'code': 403}), 403)


class Login(Resource):
    """
    Manage responses to user requests.
    """

    def post(self):
        """
        Authenticate a user.
        Returns:
            json: authentication token, expiration duration or error message.
        """
        args = validate_input({'username': True, 'password': True})
        user = User.query.filter_by(username=args['username']).first()
        if user and user.verify(args['password']):
            token = user.generate_auth_token()
            return jsonify({'Access granted': token.decode('ascii')})
        else:
            return jsonify({'Message':
                            'The username or password was invalid.'
                            'Please try again'})


class Register(Resource):
    """
    Manage responses to user requests.
    """

    def post(self):
        """
        Register a user.
        Returns:
            json: authentication token, username and duration or error message.
        """
        try:
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('username', type=str, required=True,
                                     help='Username is required', location='json')
            self.parser.add_argument('password', type=str, required=True,
                                     help='Password is required', location='json')
            args = self.parser.parse_args()
            username = args['username']
            password = args['password']
        except Exception as e:
            return {'error': str(e)}, 400
        if password == '' or username == '':
            return {'error': "Kindly enter your username and password"}
        else:
            user = User.query.filter_by(username=username).first()
            if user is not None:
                return {'error': 'Username already exists'}
            else:
                try:
                    new_user = User(username=username, password=password)
                    db.session.add(new_user)
                    db.session.commit()
                    return {'success': 'User successfully created'}, 201
                except Exception:
                    return {'error': 'Failed to create User'}
