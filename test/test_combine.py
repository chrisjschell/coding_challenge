"""Test combiner.py"""

# Standard Library
from copy import deepcopy
import json
import unittest

# Project Library
from app.tools.combine import combine
from test.input_data.combine import bitbucket, bitbucket_empty
from test.input_data.combine import github, github_empty
from test.output_data.combine import expected_empty, expected_result


class TestCombine(unittest.TestCase):
  """Test combine"""

  def test_combine(self):
    result = combine(bitbucket, github)
    result['languages']['list'].sort()
    self.assertEqual(result, expected_result)

  def test_combine_empty_results(self):
    result = combine(bitbucket_empty, github_empty)
    self.assertEqual(result, expected_empty)
