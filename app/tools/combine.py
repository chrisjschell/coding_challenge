"""Combines collected data from both Bitbucket and Github APIs"""

def combine(bitbucket, github):
  """Combines all of the information collected from the Bitbucket and Github APIS into
  a single data structure

  Args:
      bitbucket (dict): Collected data from Bitbucket API
      github ([type]): Collected data from Github API

  Returns:
      dict: Aggregated data from both Bitbucket and Github APIs
  """
  results = {'languages': {}, 'topics': {}, 'repos': {}}

  results['followers'] = bitbucket['followers'] + github['followers']

  languages = set()
  languages.update(bitbucket['languages'])
  languages.update(github['languages'])
  results['languages']['list'] = list(languages)
  results['languages']['count'] = len(results['languages']['list'])

  results['topics']['list'] = list(github['topics'])
  results['topics']['count'] = len(github['topics'])

  results['repos']['forked'] = bitbucket['repos']['forked'] + github['repos']['forked']
  results['repos']['unforked'] = bitbucket['repos']['unforked'] + github['repos']['unforked']
  results['repos']['count'] = results['repos']['forked'] + results['repos']['unforked']

  results['watchers'] = bitbucket['watchers'] + github['watchers']

  return results
