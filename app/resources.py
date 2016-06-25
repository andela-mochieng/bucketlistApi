import json
from flask_restful import reqparse, abort, Resource
from flask.ext.restful import marshal
from flask import g, jsonify, request, make_response
from sqlalchemy.exc import IntegrityError
from flask_httpauth import HTTPTokenAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from app import db
from config import config
from app.models import BucketList, User, BucketListItem
from serializers import bucketlist_serializer, bucketlistitem_serializer

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    """Receives token and verifies it, the username and the password
     must return True or False"""
    if token:
        token_serializer = Serializer(config['SECRET_KEY'])
        try:
            data = token_serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return False
        if 'id' in data:
            g.user_id = data['id']
            g.user = data['username']
            return True
    return False


@auth.error_handler
def unauthorized():
    """Alert user that a token is invalid"""
    return make_response(jsonify({'error': 'Invalid Token', 'code': 403}), 403)


class SingleBucketList(Resource):
    """
    Manage responses to bucketlists requests.
    URL:
        /api/v1.0/bucketlists/<id>/
    Methods:
        GET, PUT, DELETE
    """

    @auth.login_required
    def get(self, id):
        """
        Retrieve the bucketlist using an id.
        Args:
            id: The id of the bucketlist to be retrieved
        Returns:
            json: The bucketlist with the id.
        """

        bucketlist = BucketList.query.filter_by(created_by=g.user,
                                                id=id).first()
        if bucketlist:
            return marshal(bucketlist, bucketlist_serializer)
        else:
            return {'Message': 'the bucket list was not found.'}, 404

    @auth.login_required
    def put(self, id):
        """
        Update a bucketlist.
        Args:
            id: The id of the bucketlist to be updated
        Returns:
            json: response with success or failure message.
        """
        bucketlist = BucketList.query.filter_by(created_by=g.user,
                                                id=id).first()
        parser = reqparse.RequestParser()
        parser.add_argument('list_name', required=True,
                            help='list_name can not be blank')
        args = parser.parse_args()
        new_list_name = args['list_name']
        if new_list_name:
            bucketlist.list_name = new_list_name
            db.session.add(bucketlist)
            db.session.commit()
            return jsonify({'Message': 'Successfully updated bucketlist ',
                            'list_name': bucketlist.list_name})
        else:
            return jsonify({'Message': 'Failure. Please provide a name for the'
                            'bucketlist'})

    @auth.login_required
    def delete(self, id):
        """
        Delete a bucketlist.
        Args:
            id: The id of the bucketlist to be updated
        Returns:
            json: response with success or failure message.
        """
        bucketlist = BucketList.query.filter_by(created_by=g.user,
                                                id=id).first()
        if bucketlist:
            db.session.delete(bucketlist)
            db.session.commit()
            return {
                'message': "Successfully deleted the bucket list item: {}".format(
                    bucketlist.list_name)}
        else:
            return jsonify({'Message': 'The delete was unsuccessful.'})


class BucketLists(Resource):
    """
    Retrieve created bucketlists.
    Returns:
        json: A list of bucketlists created by the user.
    """
    @auth.login_required
    def get(self):
        args = request.args.to_dict()
        limit = int(args.get('limit', 10))
        page = int(args.get('page', 1))
        name = args.get('q')
        if name:
            results = BucketList.query. \
                filter_by(created_by=g.user, list_name=name). \
                paginate(page, limit, False).items
            if results:
                return marshal(results, bucketlist_serializer)
            else:
                return {'Message':
                        'Bucketlist ' + name + ' not found.'}, 404
        if args.keys().__contains__('q'):
            return jsonify({'Message': 'Please provide a search parameter'})

        bucketlists_page = BucketList.query.\
            filter_by(created_by=g.user).paginate(
                page=page, per_page=limit, error_out=False)
        total = bucketlists_page.pages
        next_item = bucketlists_page.has_next
        previous_item = bucketlists_page.has_prev
        if next_item:
            next_page = str(request.url_root) + 'api/v1.0/bucketlists?' + \
                'limit=' + str(limit) + '&page=' + str(page + 1)
        else:
            next_page = 'None'
        if previous_item:
            previous_page = request.url_root + 'api/v1.0/bucketlists?' + \
                'limit=' + str(limit) + '&page=' + str(page - 1)
        else:
            previous_page = 'None'
        bucketlists = bucketlists_page.items
        print(bucketlists)
        for b in bucketlists:
            print(b.bucketlist_items)
        re_quest = {'bucketlists': marshal(bucketlists, bucketlist_serializer),
                    'next_item': next_item,
                    'pages': total,
                    'previous_page': previous_page,
                    'next_page': next_page
                    }
        return re_quest

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
        except Exception as e:
            return {'error': str(e)}, 400
        if list_name == " " or list_name is None or not list_name:
            return {"message": "Enter a bucketlist name"}, 203
        try:
            if list_name:
                new_bucketlist = BucketList(
                    list_name=list_name, created_by=g.user)
                db.session.add(new_bucketlist)
                db.session.commit()
                return {'message': 'BucketList {} has been created'.format(
                    list_name)}, 201
        except IntegrityError:
            db.session.rollback()
            return {'message': "Bucket list : {} already exists".format(
                list_name)}, 203


class BucketListItems(Resource):
    """
    Manage responses to bucketlist items requests.
    URL:
        /api/v1.0/bucketlists/<id>/items/
    Methods:
        GET, POST
    """

    @auth.login_required
    def get(self, id):
        """
        Retrieve bucketlist items.
        Args:
            id: The id of the bucketlist from which to retrieve items
        Returns:
            json: response with bucketlist items.
        """
        args = request.args.to_dict()
        limit = int(args.get('limit', 0))
        page = int(args.get('page', 0))
        if limit and page:
            bucketlistitems = BucketListItem.\
                query.filter_by(bucketlist_id=id).\
                paginate(page, limit, False).all()
        else:
            bucketlistitems = BucketListItem.\
                query.filter_by(bucketlist_id=id).all()
            if bucketlistitems:
                return marshal(bucketlistitems, bucketlistitem_serializer)
            else:
                return {"message": "there are no items under this bucket list"}, 203

    @auth.login_required
    def post(self, id):
        """
        Add an item to a bucketlist.
        Args:
            id: The id of the bucketlist to add item
        Returns:
            json: response with success message and item name.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('item_name', required=True,
                            help='item_name can not be blank')
        parser.add_argument('item_description', required=True,
                            help='item_description can not be blank')
        args = parser.parse_args()
        item_name = args['item_name']
        item_description = args['item_description']
        done = False

        if item_name and item_description:
            bucketlistitem = BucketListItem(item_name=item_name,
                                            item_description=item_description,
                                            done=done, bucketlist_id=id)
            try:
                db.session.add(bucketlistitem)
                db.session.commit()
                return {'item': marshal(bucketlistitem,
                                        bucketlistitem_serializer)}, 201

            except IntegrityError:
                db.session.rollback()
                return {'error': 'The bucketlist item already exists.'}


class SingleBucketListItem(Resource):
    """
    Manage responses to bucketlist items requests.
    URL:
        /api/v1.0/bucketlist/<id>/items/<item_id>
    Methods:
        GET, POST, DELETE
    """

    @auth.login_required
    def get(self, id, item_id):
        """Method to handle all get requests to the route"""
        get_bucket_list_item = BucketListItem.query.filter_by(
            bucketlist_id=id, id=item_id).all()
        if get_bucket_list_item:
            return {'item': marshal(get_bucket_list_item, bucketlistitem_serializer)}, 200
        return {'message': "Item with id: {} doesn't exist".format(id)}, 203

    @auth.login_required
    def put(self, id, item_id):
        """
        Update a bucketlist item.
        Args:
            id: The id of the bucketlist with the item
            item_id: The id of the item being updated
        Returns:
            json: A response with a success message.
        """
        try:
            bucketlistitem = BucketListItem. \
                query.filter_by(bucketlist_id=id, id=item_id).first()
            parser = reqparse.RequestParser()
            parser.add_argument('item_name')
            parser.add_argument('item_description')
            parser.add_argument('done')
            args = parser.parse_args()
            item_name = args['item_name']
            item_description = args['item_description']
            done = args['done']
            if item_name == '' or item_name is None:
                return {'error': 'Please enter a item name'}, 203
            if item_name:
                bucketlistitem.item_name = item_name
            if item_description:
                bucketlistitem.item_description = item_description
            if done:
                if str(done).lower() == 'true':
                    done = True
                else:
                    done = False
                bucketlistitem.done = done
            else:
                return {'Message': 'No fields were changed.'}, 203

            db.session.add(bucketlistitem)
            db.session.commit()
            return {'Message': 'Successfully updated item.',
                    'item_name': bucketlistitem.item_name}, 200
        except AttributeError:
            return {'Message': 'No item matching the given id was found.'}, 203

    @auth.login_required
    def delete(self, id, item_id):
        """
        Delete a bucketlist item.
        Args:
            id: The id of the bucketlist with the item
            item_id: The id of the item being deleted
        Returns:
            json: A response with a success/ failure message.
        """
        bucketlistitem = BucketListItem. \
            query.filter_by(bucketlist_id=id, id=item_id).first()
        if bucketlistitem:
            db.session.delete(bucketlistitem)
            db.session.commit()
            return {
                'message': "Successfully deleted the bucket list item: {}".format(
                    bucketlistitem.item_name)}, 200


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
            abort(401, message='Invalid username or password')


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
            abort(401, messages="Kindly enter your username and password")
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
