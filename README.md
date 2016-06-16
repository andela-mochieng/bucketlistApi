[![Build Status](https://travis-ci.org/andela-mochieng/bucketlistApi.svg?branch=develop)](https://travis-ci.org/andela-mochieng/bucketlistApi)
[![Coverage Status](https://coveralls.io/repos/github/andela-mochieng/bucketlistApi/badge.svg?branch=develop)](https://coveralls.io/github/andela-mochieng/bucketlistApi?branch=develop)
![alt text](https://img.shields.io/badge/python-2.7-blue.svg)

# _Bucketlist API_
This is a bucketlist Api that exists for one reason, which to get you writing the list of things that you want to achieve or just get done before dying.

### Bucketlist's resources
The API resources are accessible at [localhost:8000/api/v1.0/](http://127.0.0.1:8000/api/v1.0/). They include:

| Resource URL | Methods | Description |
| -------- | ------------- | --------- |
| `/api/v1.0/` | GET  | The index |
| `/api/v1.0/auth/register/` | POST  | User registration |
|  `/api/v1.0/auth/login/` | POST | User login|
| `/api/v1.0/bucketlists/` | POST | Create a bucket list |
| `/api/v1.0/bucketlists/` | GET | Retrieve all bucketlists |
| `/api/v1.0/bucketlists/?limit=1&page=1` | GET | Retrieve one bucketlist per page|
| `/api/v1.0/bucketlists/<id>/` | GET |  A single bucket list |
| `/api/v1.0/bucketlists/<id>/` | PUT | Update a single bucket list |
| `/api/v1.0/bucketlists/<id>/` | DELETE | Delete a single bucket list |
| `/api/v1.0/bucketlists/<id>/items/` | POST |  Create items in a bucket list |
| `/api/v1.0/bucketlists/<id>/items/` | GET | Items in a bucket list |
| GET `/api/v1.0/bucketlists/<id>/items/<item_id>/` | GET, PUT, DELETE| A single bucket list item|


| Method | Description |
|------- | ----------- |
| GET | Retrieves a resource(s) |
| POST | Creates a new resource |
| PUT | Updates an existing resource |
| DELETE | Deletes an existing resource |


###### The key **libraries** used include;
1. **Flask-Restful** - a lightweight extension framework of flask that works with ORM and other libraries.to organise resources into class based views, to help serialize and display the API's models into response objects.
2. **Flask-HttpAuth** - It handle client authentication for resources where public access is denied. This API improvises this library's @auth.verify_token annotation to authenticate users via tokens.
3. **SQLAlchemy-Paginator** - A pagination library that receives an sqlalchemy query object as its first argument and a limit (results per page in int) as the second argument and creates a pagination object through which the query's content can be accessed through pages.
4. **itsdangerous** - Generate tokens from users once they log in. It's also used to identify users from tokens when authentication (in methods annotated with @auth.login_verified) is required.
5. **Coverage** - This package is used to execute the tests. It generates a test coverage report based on the lines of source code executed from the running tests.

## Installation
**__Clone this repo__**
```shell
$ git clone https://github.com/andela-mochieng/bucketlistApi.git
```

**__Nagivate to the root folder__**
```shell
$ cd bucketlistApi
```

**__Set up a virtualenv then:__**
```shell
$ pip install -r requirements.txt
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
$ python manage.py runserver
Success message: Running on http://127.0.0.1:5000/ should appear then your set.
```


## Setting up
+ Once the server is runing, navigate to http://localhost:5000//api/v1.0/ using Postman.
+ Click the header tab and set the Header to content_type: application/json.
+ Click the body tab and select on the raw option.
+ We shall be using this section for most of our requests.
+  Json format will be used in sending and receiving request.
+ After every request click on the **SEND** to view results.

**__Register a user__**

+ Set POST method on postman.
- Navigate to http://5000/api/v1.0/auth/register/
- Enter username and password in the textarea in json format.
**eg.** request: {"username":"Margie rain", "password": "sunshine"}
```shell
response : {
  "date_created": "2016-06-11 08:55:57.955005",
  "id": 1,
  "username": "Margie rain"
}
```

**__Login user__**

+ Navigate to http://5000/api/v1.0/auth/login/
**Note** the request is similar to registering a user, only the url changes
```shell
Response: {
  "Token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ2NTY0NTU2MCwiaWF0IjoxNDY1NjM1NTYwfQ.eyJpZCI6MX0.V1HZyvHjztmkp6bRKYNXMGLebSRmwoJ6twHCBBjU7dc"
```

+ An Authorization token is generated.
+ Copy the value of the token.
+ Click on the header and add a key called Authorization and paste the copied token in to the value field
+ This token will be used to access all the neccesary endpoints till it expires.
+ A token will last for not more than 10 minutes
**Note:** Authentication relies on the token all other pages can only be accessed once a valid token is presented

**__Add Bucketlist__**

Navigate to http://localhost:5000/api/v1.0/bucketlists/

+ Set request method to POST
+ Make sure the token is set in the Header if you have logged in
**eg.** request : { "list_name": "Bucketlist 1" }
```shell
response : {
  "message": "BucketList Bucketlist 1 has been created"
}
```

**__View all bucketlists__**

+ Set request method to GET
**NB**: Pagination kicks in when you have more items

+ To see it in action: create more bucket list names then:
+ Set the (limit) number og bucket list names you want to view per page eg.
 http://localhost:5000/api/v1.0/bucketlists/?limit=1&page=2
```shell
 response: {
  "bucketlists": [
    {
      "created_by": "1",
      "date_created": "Sat, 11 Jun 2016 09:13:44 -0000",
      "date_modified": "Sat, 11 Jun 2016 09:13:44 -0000",
      "id": 2,
      "list_name": "Bucketlist 1"
    }
  ],
  "next_item": true,
  "next_page": "http://127.0.0.1:5000/api/v1.0/bucketlists?limit=1&page=3",
  "pages": 5,
  "previous_page": "http://127.0.0.1:5000/api/v1.0/bucketlists?limit=1&page=1"
}
```

**__View  a single bucketlist__**
**e.g** request: Navigate to http://localhost:5000/api/v1.0/bucketlist/1/

+ Set request method to GET
```shell
$ response : {
  "created_by": "1",
  "date_created": "Sat, 11 Jun 2016 09:13:18 -0000",
  "date_modified": "Sat, 11 Jun 2016 09:13:18 -0000",
  "id": 1,
  "list_name": "Fly an aeroplane"
}
```
Continue using the API endpoints from the table above to test the bucketlist.

To run tests:
```shell
$ nosetests --with-coverage
```