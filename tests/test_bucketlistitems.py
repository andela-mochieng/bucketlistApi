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

    def test_creation_of_bucketlist_items(self):
        """Test retrieving all bucket list items"""
        self.create_bucketlist()

        data = {'item_name': 'bucketlist_item one', 'item_description':'First item description'}
        self.client.post('/api/v1.0/bucketlists/1/items/', data=data,
                    headers=self.token)
        response = self.app.get('/api/v1.0/bucketlists/1/items/', headers=self.token)
        self.assert200(response)

    # def test_bucket_list_item_creation_fails_when_no_info_is_provided(self):
    #     """tests that creation of a bucket-list-item fails
    #     when no info is sent"""
    #     response = self.client.post('/api/v1.0/bucketlists/<id>/items/',
    #         data=json.dumps({'item_name': ''}), headers=self.token)
    #     self.assertEqual(response.status_code, 203)
    #     self.assertIn("item_description can not be blank", response.data)

    # def test_updating_of_a_bucketlist_item(self):
    #     """Test updating bucketlist items."""
    #     self.create_bucketlist()
    #     data = {'item_name': 'bucketlist item 1',
    #                 'item_description':'First item description 1'}
    #     print(self.token)
    #     response = self.client.put('/api/v1.0/bucketlists/1/items/', data=data,
    #                     headers=self.token)
    #     print(response.status_code)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.data),
    #                      {'item_name': data['item_name'],
    #                       'Message': 'Successfully updated item.'})
    #
    # def test_bucketlist_items_can_be_deleted(self):
    #     self.create_bucketlist()
    #     data = {'item_name': 'bucketlist item 1',
    #             'item_description': 'First item description 1'}
    #     self.app.post('/api/v1.0/bucketlists/1/items/1', data=data,
    #                   headers=self.token)
    #     response = self.client.delete('/api/v1.0/bucketlists/1/items/1/',
    #                            headers=self.token)
    #     self.assert200(response)