from flask import url_for
import json
from test_config import BaseTestCase
from manage import db, app
from app.models import BucketList, User, BucketListItem

class TestBucketListItems(BaseTestCase):
    """Test bucket list items"""


    def create_bucketlist(self):
        """Test creation of a new bucketlist to test bucketlist item actions"""
        data = {'list_name': "Bucketlist 1"}
        response = self.client.post('/api/v1.0/bucketlists/1/items/', data=data, headers=self.token)
        if response.status_code == 200:
            return True
        return False

    def create_bucketlist_item(self):
        resp_items=self.client.post('/api/v1.0/bucketlists/1/items/',
                                data=json.dumps(
                                    {'item_name': 'bucketlist item 1',
                                     'item_description': 'First item description 1',
                                     'done': 'False'}),
                                content_type="application/json",
                                headers=self.token)
        return resp_items


    def test_creation_of_bucketlist_items(self):
        """Test retrieving all bucket list items"""
        self.create_bucketlist()
        data = {'item_name': 'bucketlist_item one', 'item_description':'First item description'}
        self.client.post('/api/v1.0/bucketlists/1/items/', data=data,
                    headers=self.token)
        response = self.client.get('/api/v1.0/bucketlists/1/items/',
                                headers=self.token)
        self.assert200(response)

    def test_bucket_list_item_creation_fails_when_no_info_is_provided(self):
        """tests that creation of a bucket-list-item fails
        when no info is sent"""
        data = {'item_name': ''}
        response = self.client.post('/api/v1.0/bucketlists/1/items/',
            data=data, headers=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn("item_description can not be blank", response.data)

    def test_updating_of_a_bucketlist_item(self):
        """Test updating bucketlist items."""
        self.create_bucketlist()
        self.create_bucketlist_item()
        response = self.client.put('/api/v1.0/bucketlists/1/items/1',
                                   data=json.dumps({'item_name': 'bucketlist '
                                                                 'item one',
                    'item_description':'First item description 1',
                    'done': 'False'}), content_type="application/json",
                        headers=self.token)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated item", response.data)


    def test_bucketlist_items_can_be_deleted(self):
        self.create_bucketlist()
        self.create_bucketlist_item()
        data = {'item_name': 'bucketlist item 1',
                'item_description': 'First item description 1'}
        response=self.client.delete('/api/v1.0/bucketlists/1/items/1',
                                    data=data,
                      headers=self.token)
        self.assert200(response)

    def test_unauthorized_access(self):
        """Test unauthorised access."""
        resp = self.client.get('/api/v1.0/bucketlists/1/items/')
        self.assert403(resp)