"""Bitbucket API compiler"""

# Standard Library
import logging

# Third Party
import requests

logger = logging.getLogger('user_profiles_api.bitbucket')
logger.setLevel(logging.INFO)


class Bitbucket:
  """Interacts with Bitbucket API to collect necessary information from a given organiation. The
  `version` input is currently set to default to '2.0', which is the current Bitbucket API version.
  In the future this class will serve as the base Bitbucket API class which will instantiate subclasses
  based on the desired version of Bitbucket to be aggregated. This class aggregates the following information:
    * Total number of public repos, sorted by whether it is an original or forked repo
    * Total number of followers
    * Total number watchers
    * List of all unique languages across all repos

  Attributes:
    followers (int): Number of followers
    languages (set): Languages used across all repos
    org (str): Github organization name to collect information on
    repos (dict): Repository information sorted by forked and unforked
    results (dict): Final aggregated information
    url (str): Base Bitbucket API URL
    watchers (int): Number of watchers

  Returns:
    results (dict): Aggregated information
"""
  def __init__(self, org, version='2.0'):
    self.followers = 0
    self.languages = set()
    self.org = org
    self.repos = {'forked': 0, 'unforked': 0}
    self.results = {}
    self.url = f'https://api.bitbucket.org/{version}'
    self.watchers = 0


  def get_all_results(self, link, data=True):
    """Gets all of the results by continuing to make API calls through the pagination
    information provided by Bitbucket

    Args:
        link (str): URL for desired API call
        data (bool, optional): Determines if the desired information to be returned is
        the actual data associated from the API call or the number of return values, which is
        used for several information categories. Defaults to True.

    Returns:
        dict|int: If the desired return value is the actual data from the API call the return
        format is a list and if the desired return value is the number of return values then that is
        returned in the form of an integer
    """
    try:
      if data:
        paginated_results = []
      else:
        paginated_results = 0

      results_remaining = True
      while results_remaining:
        page_results = self.make_api_call(link)
        paginated_results += self.get_result(page_results, data)
        link = page_results.get('next')
        if not link:
          results_remaining = False
    except ValueError:
      pass

    return paginated_results


  def get_followers_count(self):
    """Updates the followers count for the given organization by getting all of the results through
    API calls and counting the number of results"""
    url = f'{self.url}/teams/{self.org}/followers?pagelen=100'
    results = self.get_all_results(url, data=False)
    self.followers += results


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
    self.results['watchers'] = self.watchers

    return self.results


  def process_repos(self):
    """Obtain all repository data and then update the aggregated categories either on a
    per repo or per organization basis
    """
    url = f'{self.url}/repositories/{self.org}?pagelen=100'
    repos = self.get_all_results(url, data=True)

    for repo in repos:
      self.update_languages(repo['language'])
      self.update_repo_count(repo['links']['forks']['href'])
      self.update_watchers_count(repo['name'])
    self.get_followers_count()


  def update_languages(self, language):
    self.languages.add(language)


  def update_repo_count(self, link):
    """Update the repository count and sorts by forked and unforked on a per repository basis

    Args:
        link (str): The URL associated with obtaining fork information for a given repository

    Raises:
        ValueError: If the connection is made the URL is invalid this is raised
    """
    try:
      fork = self.make_api_call(link)
      if fork['values']:
        self.repos['forked'] += 1
      else:
        self.repos['unforked'] += 1
    except ValueError:
      self.repos['unforked'] += 1


  def update_watchers_count(self, repo):
    """Update the watchers count for all repositories

    Args:
        repo (str): Repository name to obtain watcher information for all repositories
    """
    repo = '-'.join(repo.split())
    url = f'{self.url}/repositories/{self.org}/{repo}/watchers?pagelen=100'
    results = self.get_all_results(url, data=False)
    self.watchers += results


  @staticmethod
  def get_result(page_results, data):
    """Obtain either the data from an API call or the number of data points from the API call

    Args:
        page_results (dict): API return data
        data (boolean): Flag to determine if the desired return value is the actual data from an API
        call or the number of return values

    Returns:
        list|int: Returns either the list of data or the number data values in the form of an int
    """
    try:
      if data:
        return page_results['values']
      return len(page_results['values'])
    except KeyError:
      if data:
        return []
      return 0


  @staticmethod
  def make_api_call(url):
    """Makes an API call to the provided URL. If a connection cannot be made successfully it raises a
    connection error and if the connection is successful but the url is invalid a value error is raised

    Args:
        url (str): URL for the desired API call

    Raises:
        ValueError: If the connection is valid but the URL is incorrect this is raised
        ConnectionResetError: If the connection is invalid this is raised

    Returns:
        dict: API call data
    """
    try:
      res = requests.get(url)
      if res.ok:
        return res.json()
      logging.error('Unable to retrieve request for URL: %s', url)
      raise ValueError
    except requests.exceptions.RequestException as exception:
      logger.error('Connection not made to Bitbucket API')
      raise ConnectionResetError(exception)
