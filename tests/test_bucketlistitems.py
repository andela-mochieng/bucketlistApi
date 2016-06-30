
import json
from test_config import BaseTestCase



class TestBucketListItems(BaseTestCase):
    """Test bucket list items"""
    
    def create_bucketlist(self):
        """Test creation of a new bucketlist to test bucketlist item actions"""
        data = {'list_name': "Bucketlist 1"}
        response = self.client.post(
            '/api/v1.0/bucketlists/1/items/', data=data, headers=self.token)
        if response.status_code == 200:
            return True
        return False

    def create_bucketlist_item(self):
        """Creation of a bucket list item called by other tests"""
        resp_items = self.client.post('/api/v1.0/bucketlists/1/items/',
                                      data=json.dumps(
                                          {'item_name': 'bucketlist item 1',
                                           'item_description': 'First item description 1',
                                           'done': 'False'}),
                                      content_type="application/json",
                                      headers=self.token)
        return resp_items

    def test_bucket_list_item_creation_fails_when_no_info_is_provided(self):
        """tests that creation of a bucket-list-item fails when no info is sent"""
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
                                                    'item_description': 'First item description 1',
                                                    'done': 'False'}), content_type="application/json",
                                   headers=self.token)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated item", response.data)

    def test_bucketlist_items_can_be_deleted(self):
        """Test that a user can delete their bucket list"""
        self.create_bucketlist()
        self.create_bucketlist_item()
        data = {'item_name': 'bucketlist item 1',
                'item_description': 'First item description 1'}
        response = self.client.delete('/api/v1.0/bucketlists/1/items/1',
                                      data=data,
                                      headers=self.token)
        self.assert200(response)

    def test_that_a_list_is_not_updated_when_similar_items_are_submittted(
            self):
        """Test_that_a_list_is_not_updated_when_similar_items_are_submittted."""
        self.create_bucketlist()
        self.create_bucketlist_item()
        data = {'item_name': 'bucketlist_item one',
                'item_description': 'First item description'}

        response = self.client.put('/api/v1.0/bucketlists/1/items/1',
                                   data=data,
                                   headers=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertIn("No fields were changed", response.data)
