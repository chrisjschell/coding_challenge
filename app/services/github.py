"""Github API compiler"""

# Standard Library
import logging
import re

# Third Party
import requests

logger = logging.getLogger('user_profiles_api.github')
logger.setLevel(logging.INFO)


class Github:
  """Interacts with Github API to collect necessary information from a given organiation. Since
  Github does not directly version their API the `version` input is more of a placeholder
  rather than being inserted into the URL directly. This class aggregates the following information:
    * Total number of public repos, sorted by whether it is an original or forked repo
    * Total number of followers
    * Total number watchers
    * List of all unique languages across all repos
    * List of repo topics

  Attributes:
    followers (int): Number of followers
    languages (set): Languages used across all repos
    org (str): Github organization name to collect information on
    repos (dict): Repository information sorted by forked and unforked
    results (dict): Final aggregated information
    topics (set): Topics across all repos
    url (str): Base Github API URL
    watchers (int): Number of watchers

  Returns:
    results (dict): Aggregated information
"""
  def __init__(self, org, version=1.0):
    self.followers = 0
    self.languages = set()
    self.org = org
    self.repos = {'forked': 0, 'unforked': 0}
    self.results = {}
    self.topics = set()
    self.url = 'https://api.github.com'
    self.watchers = 0


  def get_all_repos(self, link):
    """Collects the data for all the repos for the given organization

    Args:
        link (str): URL to collect repository data

    Returns:
        list: List of all collected repository data
    """
    results = []
    try:
      data = self.make_api_call(link)
      results += data['results']
      if data['headers'].get('link'):
        total_pages = self.get_total_pages(data['headers']['link'])
        for page in range(2, (total_pages + 1)):
          url = f'{link}&page={page}'
          next_data = self.make_api_call(url)
          results += next_data['results']
    except ValueError:
      pass

    return results


  def get_followers_count(self):
    """Updates the followers count for the given organization. Gets the total number of pages of followers
    using the links provided by Github. The `per_page` attribute is set to '0' on the initial
    API call so that the total number of pages equals the total number of followers which means no additional
    API calls are required"""
    try:
      url = f'{self.url}/users/{self.org}/followers?per_page=1'
      data = self.make_api_call(url)
      if data.get('headers') and data['headers'].get('link'):
        link_header = data['headers']['link']
        followers = int(re.findall('page=(.*)>;', link_header)[-1].split('page=')[-1])
        self.followers += followers
      else:
        self.followers += len(data['results'])
    except ValueError:
      pass


  def make_response(self):
    """Collects all information from all of the repositories of the given organization,
    formats the collected results and returns the results. If a connection error should occur
    all return values are defaulted to zero or none

    Returns:
        dict: Formatted results
    """
    logger.info('Collecting data')
    try:
      self.process_repos()
    except ConnectionResetError:
      pass

    logger.info('Processing results')
    self.results['followers'] = self.followers
    self.results['languages'] = self.languages
    self.results['repos'] = self.repos
    self.results['topics'] = list(self.topics)
    self.results['watchers'] = self.watchers

    return self.results


  def process_repos(self):
    """Obtain all repository data and then update the aggregated categories either on a
    per repo or per organization basis
    """
    url = f'{self.url}/orgs/{self.org}/repos?per_page=100'
    results = self.get_all_repos(url)

    for repo in results:
      self.update_languages(repo['name'])
      self.update_repo_count(repo['fork'])
      self.update_topics(repo.get('topics'))
      self.update_watchers_count(repo['watchers'])
    self.get_followers_count()


  def update_languages(self, repo):
    """Update the list of unique languages associated with all of the repos on a
    per repository basis

    Args:
        repo (str): Name of the repo in order to obtain the language information
    """
    try:
      url = f'{self.url}/repos/{self.org}/{repo}/languages'
      headers = {'accept': 'application/vnd.github.v3+json'}
      data = self.make_api_call(url, headers)
      languages = list(data['results'].keys())
      for entry in range(len(languages)):
        languages[entry] = languages[entry].lower()
      self.languages.update(languages)
    except  ValueError:
      pass


  def update_repo_count(self, forked):
    """Update the repository count and sorts by forked and unforked on a per repository basis

    Args:
        forked (boolean): If True the repo is forked and unforked if False
    """
    if forked:
      self.repos['forked'] += 1
    else:
      self.repos['unforked'] += 1


  def update_topics(self, topics):
    """Update the unique list of topics associated with each repository of the given
    organization

    Args:
        topics (list): Obtain a list of topics per repository and update the set
    """
    if topics:
      self.topics.update(topics)


  def update_watchers_count(self, watchers):
    """Update the watchers count on a per repository basis

    Args:
        watchers (int): Number of watchers per repository
    """
    self.watchers += watchers


  @staticmethod
  def get_total_pages(link_header):
    """Parses the link header provided by Github to obtain the total number of pages required
    to paginate through to obtain all of the repository data

    Args:
        link_header (str): The header information from the `link` value provided by Github

    Returns:
        int: The total number of pages associated with a given Github API call
    """
    total_pages = int(re.findall('page=(.*)>;', link_header)[-1].split('page=')[-1])

    return total_pages


  @staticmethod
  def make_api_call(url, headers={}):
    """Makes an API call to the provided URL. If a connection cannot be made successfully it raises a
    connection error and if the connection is successful but the url is invalid a value error is raised

    Args:
        url (str): URL for the desired API call

    Raises:
        ValueError: If the connection is valid but the URL is incorrect this is raised
        ConnectionResetError: If the connection is invalid this is raised

    Returns:
        dict: API call data and the associated headers
    """
    try:
      res = requests.get(url, headers=headers)
      if res.ok:
        return {'results': res.json(), 'headers': res.headers}
      logging.error('Unable to retrieve request for URL: %s', url)
      raise ValueError
    except requests.exceptions.RequestException as exception:
      logger.error('Connection not made to Github API')
      raise ConnectionResetError(exception)
