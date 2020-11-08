"""Test Bitbucket API aggregator"""

# Standard Library
import unittest
from unittest.mock import Mock, patch

# Third Party
import requests

# Project Library
from app.services.bitbucket import Bitbucket

class TestBitbucket(unittest.TestCase):
  """Test Bitbucket API Aggregator Class"""

  @patch('requests.get')
  def test_get_all_results_data(self, mock_get):
    mock_responses = [Mock(), Mock()]
    mock_responses[0].json.return_value = {'values': [{'repo': 'data'}], 'next': 'url'}
    mock_responses[1].json.return_value = {'values': [{'repo': 'data'}]}
    mock_get.side_effect = mock_responses

    b = Bitbucket('test')
    results = b.get_all_results('url')
    self.assertEqual(results, [{'repo': 'data'}, {'repo': 'data'}])


  @patch('requests.get')
  def test_get_all_results_count(self, mock_get):
    mock_responses = [Mock(), Mock()]
    mock_responses[0].json.return_value = {'values': [{'repo': 'data'}], 'next': 'url'}
    mock_responses[1].json.return_value = {'values': [{'repo': 'data'}]}
    mock_get.side_effect = mock_responses

    b = Bitbucket('test')
    results = b.get_all_results('url', data=False)
    self.assertEqual(results, 2)


  @patch('requests.get')
  def test_get_followers_count(self, mock_get):
    mock_get.return_value.json.return_value = {'values': [{'followers': 'count'}]}
    b = Bitbucket('test')
    b.get_followers_count()
    self.assertEqual(b.followers, 1)


  def test_get_result_data(self):
    result = Bitbucket.get_result({'values':[{'api': 'data'}]}, True)
    self.assertEqual(result, [{'api': 'data'}])


  def test_get_result_count(self):
    result = Bitbucket.get_result({'values':[{'api': 'data'}]}, False)
    self.assertEqual(result, 1)


  @patch('requests.get')
  def test_make_api_call(self, mock_get):
    mock_get.return_value.headers = {}
    mock_get.return_value.json.return_value = [{}]
    result = Bitbucket.make_api_call('url')
    self.assertEqual(result, [{}])


  @patch('requests.get')
  def test_make_api_call_invalid_request(self, mock_get):
    mock_get.return_value.ok = False
    with self.assertRaises(ValueError):
      Bitbucket.make_api_call('url')


  @patch('requests.get')
  def test_make_api_call_no_connection(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    with self.assertRaises(ConnectionResetError):
      Bitbucket.make_api_call('url')


  @patch('requests.get')
  def test_make_response(self, mock_get):
    mock_responses = [Mock(), Mock(), Mock(), Mock()]

    # get_all_results
    mock_responses[0].json.return_value = {'values': [{
        'language': 'python',
        'links': {'forks': {'href': 'url'}},
        'name': 'test_repo'
    }]}

    # update_repo_count
    mock_responses[1].json.return_value = {'values': [{'fork': 'data'}]}

    # update_watchers_count
    mock_responses[2].json.return_value = {'values': [{'watchers': 'data'}]}

    # get_followers_count
    mock_responses[3].json.return_value = {'values': [{'followers': 'count'}]}

    mock_get.side_effect = mock_responses

    b = Bitbucket('test')
    result = b.make_response()
    self.assertEqual(result['followers'], 1)
    self.assertEqual(result['languages'], {'python'})
    self.assertEqual(result['repos']['forked'], 1)
    self.assertEqual(result['repos']['unforked'], 0)
    self.assertEqual(result['watchers'], 1)


  @patch('requests.get')
  def test_make_response_no_connection(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    b = Bitbucket('test')
    results = b.make_response()
    self.assertEqual(results['followers'], 0)
    self.assertEqual(results['repos']['forked'], 0)
    self.assertEqual(results['repos']['unforked'], 0)
    self.assertEqual(results['watchers'], 0)


  @patch('requests.get')
  def test_process_repos(self, mock_get):
    mock_responses = [Mock(), Mock(), Mock(), Mock()]

    # get_all_results
    mock_responses[0].json.return_value = {'values': [{
        'language': 'python',
        'links': {'forks': {'href': 'url'}},
        'name': 'test_repo'
    }]}

    # update_repo_count
    mock_responses[1].json.return_value = {'values': [{'fork': 'data'}]}

    # update_watchers_count
    mock_responses[2].json.return_value = {'values': [{'watchers': 'data'}]}

    # get_followers_count
    mock_responses[3].json.return_value = {'values': [{'followers': 'count'}]}

    mock_get.side_effect = mock_responses

    b = Bitbucket('test')
    b.process_repos()
    self.assertEqual(b.followers, 1)
    self.assertEqual(b.languages, {'python'})
    self.assertEqual(b.repos['forked'], 1)
    self.assertEqual(b.repos['unforked'], 0)
    self.assertEqual(b.watchers, 1)



  def test_update_language(self):
    b = Bitbucket('test')
    b.update_languages('python')
    self.assertEqual(b.languages, {'python'})


  @patch('requests.get')
  def test_update_repo_count_forked(self, mock_get):
    mock_get.return_value.json.return_value = {'values': [{'fork': 'data'}]}
    b = Bitbucket('test')
    b.update_repo_count('url')
    self.assertEqual(b.repos['forked'], 1)
    self.assertEqual(b.repos['unforked'], 0)


  @patch('requests.get')
  def test_update_repo_count_unforked(self, mock_get):
    mock_get.return_value.json.return_value = {'values': []}
    b = Bitbucket('test')
    b.update_repo_count('url')
    self.assertEqual(b.repos['forked'], 0)
    self.assertEqual(b.repos['unforked'], 1)


  @patch('requests.get')
  def test_update_watchers_count(self, mock_get):
    mock_get.return_value.json.return_value = {'values': [{'watchers': 'data'}]}
    b = Bitbucket('test')
    b.update_watchers_count('test repo')
    self.assertEqual(b.watchers, 1)
