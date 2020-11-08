"""Test Github API aggregator"""

# Standard Library
import unittest
from unittest.mock import Mock, patch

# Third Party
import requests

# Project Library
from app.services.github import Github


LINK_HEADER = '<https://api.github.com/organizations/216758/repos?per_page=1&page=1>; rel="next", '\
  '<https://api.github.com/organizations/216758/repos?per_page=1&page=2>; rel="last"'


class TestGithub(unittest.TestCase):
  """Test Github API Aggregator Class"""

  @patch('requests.get')
  def test_get_all_repos(self, mock_get):
    mock_get.return_value.headers = {'link': LINK_HEADER}
    mock_get.return_value.json.return_value = [{'repo': 'data'}]
    g = Github('test')
    results = g.get_all_repos('url')
    self.assertEqual(results, [{'repo': 'data'}, {'repo': 'data'}])


  @patch('requests.get')
  def test_get_followers_count(self, mock_get):
    mock_get.return_value.headers = {'link': LINK_HEADER}
    g = Github('test')
    g.get_followers_count()
    self.assertEqual(g.followers, 2)


  def test_get_total_pages(self):
    result = Github.get_total_pages(LINK_HEADER)
    self.assertEqual(result, 2)


  @patch('requests.get')
  def test_make_api_call(self, mock_get):
    mock_get.return_value.headers = {}
    mock_get.return_value.json.return_value = [{}]
    result = Github.make_api_call('url')
    self.assertEqual(result, {'results': [{}], 'headers': {}})


  @patch('requests.get')
  def test_make_api_call_invalid_request(self, mock_get):
    mock_get.return_value.ok = False
    with self.assertRaises(ValueError):
      Github.make_api_call('url')


  @patch('requests.get')
  def test_make_api_call_no_connection(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    with self.assertRaises(ConnectionResetError):
      Github.make_api_call('url')


  @patch('requests.get')
  def test_make_response(self, mock_get):
    mock_responses = [Mock(), Mock(), Mock()]

    # get_all_repos
    mock_responses[0].headers = {}
    mock_responses[0].json.return_value = [{
        'name': 'test_repo',
        'fork': True,
        'topics': ['flask'],
        'watchers': 1
    }]

    # update_languages
    mock_responses[1].headers = {}
    mock_responses[1].json.return_value = {'php': 1}

    # get_followers_count
    mock_responses[2].headers = {}
    mock_responses[2].json.return_value = [{}]

    mock_get.side_effect = mock_responses

    g = Github('test')
    results = g.make_response()
    self.assertEqual(results['followers'], 1)
    self.assertEqual(results['repos']['forked'], 1)
    self.assertEqual(results['repos']['unforked'], 0)
    self.assertEqual(results['topics'], ['flask'])
    self.assertEqual(results['watchers'], 1)


  @patch('requests.get')
  def test_make_response_no_connection(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()
    g = Github('test')
    results = g.make_response()
    self.assertEqual(results['followers'], 0)
    self.assertEqual(results['repos']['forked'], 0)
    self.assertEqual(results['repos']['unforked'], 0)
    self.assertEqual(results['topics'], [])
    self.assertEqual(results['watchers'], 0)


  @patch('requests.get')
  def test_process_repos(self, mock_get):
    mock_responses = [Mock(), Mock(), Mock()]

    # get_all_repos
    mock_responses[0].headers = {}
    mock_responses[0].json.return_value = [{
        'name': 'test_repo',
        'fork': True,
        'topics': ['flask'],
        'watchers': 1
    }]

    # update_languages
    mock_responses[1].headers = {}
    mock_responses[1].json.return_value = {'php': 1}

    # get_followers_count
    mock_responses[2].headers = {}
    mock_responses[2].json.return_value = [{}]

    mock_get.side_effect = mock_responses

    g = Github('test')
    g.process_repos()
    self.assertEqual(g.followers, 1)
    self.assertEqual(g.repos['forked'], 1)
    self.assertEqual(g.repos['unforked'], 0)
    self.assertEqual(g.topics, {'flask'})
    self.assertEqual(g.watchers, 1)


  @patch('requests.get')
  def test_update_languages(self, mock_get):
    mock_get.return_value.json.return_value = {'PHP': 1}
    g = Github('test')
    g.update_languages('test_repo')
    self.assertEqual(g.languages, {'php'})


  def test_update_repo_count(self):
    g = Github('test')
    g.update_repo_count(True)
    g.update_repo_count(False)
    self.assertEqual(g.repos['forked'], 1)
    self.assertEqual(g.repos['unforked'], 1)


  def test_update_topics(self):
    g = Github('test')
    g.update_topics(['topic 1'])
    self.assertEqual(g.topics, {'topic 1'})


  def test_update_watchers(self):
    g = Github('test')
    g.update_watchers_count(1)
    self.assertEqual(g.watchers, 1)
