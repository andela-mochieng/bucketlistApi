from collections import OrderedDict
from flask_restful import reqparse, abort, Resource
from flask.ext.restful import marshal
from flask import g, jsonify, request, make_response
from sqlalchemy.exc import IntegrityError
from app import db
from config import Config
from config import config
from app.models import BucketList, User, BucketListItem
from flask_httpauth import HTTPTokenAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    if token:
        token_serializer = Serializer(config['SECRET_KEY'])
        try:
            data = token_serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return False
        if 'id' in data:
            g.user = data['id']
            return True
    return False



@auth.error_handler
def unauthorized():
    """Alert user that a token is invalid"""
    return make_response(jsonify({'error': 'Invalid Token', 'code': 403}), 403)

class BucketLists(Resource):
    """
    Retrieve created bucketlists.
    Returns:
        json: A list of bucketlists created by the user.
    """
    # @auth.login_required

    # def get(self):
    #     args = request.args.to_dict()
    #     limit = int(args.get('limit', 10))
    #     page = int(args.get('page', 1))
    #     name = args.get('q')
    #     if name:
    #         results = BucketList.query.\
    #             filter_by(created_by=g.user.id, list_name=name).\
    #             paginate(page, limit, False).items
    #         if results:
    #             return marshal(results, bucketlist_serializer)
    #         else:
    #             return {'Message':
    #                     'Bucketlist ' + name + ' not found.'}, 404
    #     if args.keys().__contains__('q'):
    #         return jsonify({'Message': 'Please provide a search parameter'})

    #     bucketlists_page = BucketList.query.\
    #         filter_by(created_by=g.user.id).paginate(
    #             page=page, per_page=limit, error_out=False)
    #     total = bucketlists_page.pages
    #     next_item = bucketlists_page.next_item
    #     previous_item = bucketlists_page.has_prev
    #     if next_item:
    #         next_page = str(request.url_root) + 'api/v1.0/bucketlists?' + \
    #             'limit=' + str(limit) + '&page=' + str(page + 1)
    #     else:
    #         next_page = 'None'
    #     if previous_item:
    #         previous_page = request.url_root + 'api/v1.0/bucketlists?' + \
    #             'limit=' + str(limit) + '&page=' + str(page - 1)
    #     else:
    #         previous_page = 'None'
    #     bucketlists = bucketlists_page.items

    #     quest = {'bucketlists': marshal(bucketlists, bucketlist_serializer),
    #              'next_item': next_item,
    #              'pages': total,
    #              'previous_page': previous_page,
    #              'next_page': next_page
    #              }
    #     return quest

    @auth.login_required
    def post(self):
        """
        Create and save a new bucketlist.
        Returns:
            A response indicating success.
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('list_name', required=True,
                                help='list_name can not be blank')
            args = parser.parse_args()
            list_name = args['list_name']
            print(list_name)
        except Exception as e:
            return {'error': str(e)}, 400
        # import ipdb; ipdb.set_trace()
        if list_name == " " or list_name is None or not list_name:
            return abort(203, msg="Enter a bucketlist name")
        check_bucket_list_name = BucketList.query.filter_by(
            list_name=list_name, created_by=g.user).first()
        if check_bucket_list_name and check_bucket_list_name is not None:
            return {'message': "bucket list : {} already exists".format(list_name)}, 203
        else:
            if list_name:
                new_bucketlist = BucketList(
                    list_name=list_name, created_by=g.user)
                db.session.add(new_bucketlist)
                db.session.commit()
                return new_bucketlist.get(), 201


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
        try:
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('username', type=str, required=True,
                                     help='Unauthorized Access', location='json')
            self.parser.add_argument('password', type=str, required=True,
                                     help='Unauthorized Access', location='json')
            args = self.parser.parse_args()

        except Exception as e:
            return {'error': str(e)}, 401
        user = User.query.filter_by(username=args['username']).first()
        if user and user.verify_password(args['password']):
            return {'Token': user.generate_auth_token()}, 200
        else:
            abort(403, message='Invalid username or password')


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
                                     help='Unauthorized Access', location='json')
            self.parser.add_argument('password', type=str, required=True,
                                     help='Unauthorized Access', location='json')
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
                abort(401, messages="User already exists")
            else:
                try:
                    new_user = User(username=username, password=password)
                    db.session.add(new_user)
                    db.session.commit()
                    return new_user.get(), 201
                except Exception:
                    return {'error': 'Failed to create User'}
