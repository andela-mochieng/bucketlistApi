from flask import url_for
import json
from test_config import BaseTestCase
from manage import db, app
from app.models import BucketList, User, BucketListItem


class BucketListTest(BaseTestCase):
    """This class contains all bucketlist tests"""

    def test_necessary_response_is_authorized(self):
        """Test token in the header is valid."""
        response = self.app.post('/api/v1.0/bucketlists/',
                                 headers=self.token)
        self.assert400(response)

    def test_succesful_bucketlist_creation_with_correct_info(self):
        """Test succesful_bucketlist_creation_with_correct_info """
        data = {"list_name": "Bucketlist 2"}
        response = self.client.post(url_for('bucketlists'),
                                    data=data,
                                    headers=self.token
                                    )
        self.assertEqual(response.status_code, 201)
        self.assertIn(data['list_name'], response.data)

    def test_bucket_list_creation_fails_when_no_info_is_provided(self):
        """Tests that creation of a bucket-list fails when wrong info is sent"""
        data = {"list_name": ""}
        response = self.client.post('/api/v1.0/bucketlists/',
                                    data=data,
                                    headers=self.token
                                    )
        self.assertEqual(response.status_code, 203)
        self.assertIn("Enter a bucketlist name", response.data)

    def test_bucket_list_creation_fails_when_same_bucket_list_is_provided(self):
        """Tests that creation of a bucket-list fails when same info is sent"""
        response = self.client.post(url_for('bucketlists'),
                                    data=json.dumps({'list_name': 'Bucketlist 1',
                                                     'created_by': 2}),
                                    headers=self.token,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 203)
        self.assertIn(
            "Bucket list : Bucketlist 1 already exists", response.data)

    def test_retrieval_of_bucket_lists(self):
        """tests that there exists bucket-lists"""
        response = self.client.get('/api/v1.0/bucketlists/',
                                   headers=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.bl_name, response.data)

    def test_update_of_single_bucket_list_succeeds(self):
        """Tests that updating a bucket list succeeds when
        right info is sent"""
        response = self.client.put('/api/v1.0/bucketlists/1/',
                                   data=dict(
                                       list_name='Bucket List One'),
                                   headers=self.token
                                   )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated bucketlist",
                      response.data)
