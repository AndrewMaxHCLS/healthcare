"""Tests for healthcare.deploy.utils.utils.py.

These tests check that the module is free from syntax errors.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags
from absl.testing import absltest

from deploy.utils import utils

FLAGS = flags.FLAGS


class UtilsTest(absltest.TestCase):

  def test_merge_two_config_dicts(self):
    dict1 = {'a': {'aa': [1, 2, 3], 'ab': 5, 'ac': {'aca': 'xx', 'acb': 'yy'}}}
    dict2 = {'a': {'aa': [3, 4.5], 'ac': {'aca': 'XXX', 'acc': 'ZZZ'}}}
    expect_merge_dict = {
        'a': {
            'aa': [1, 2, 3, 3, 4.5],
            'ab': 5,
            'ac': {
                'aca': 'xx',
                'acb': 'yy',
                'acc': 'ZZZ'
            }
        }
    }
    utils.merge_two_config_dicts(dict1, dict2, True)
    self.assertEqual(expect_merge_dict, dict1)

  def test_merge_two_config_dicts_conflict(self):
    dict1 = {'a': {'aa': [1, 2, 3], 'ab': 5, 'ac': {'aca': 'xx', 'acb': 'yy'}}}
    dict2 = {'a': {'aa': [3, 4.5], 'ac': {'aca': 'XXX', 'acc': 'ZZZ'}}}
    with self.assertRaises(TypeError):
      utils.merge_two_config_dicts(dict1, dict2, False)

  def test_load_config_spanned_configs(self):
    project_yaml = ('deploy/samples/'
                    'project_with_remote_audit_logs.yaml')
    input_yaml_path = utils.normalize_path(project_yaml)
    dict1 = utils.load_config(input_yaml_path)

    project_yaml = (
        'deploy/samples/spanned_configs/root.yaml')
    input_yaml_path = utils.normalize_path(project_yaml)
    dict2 = utils.load_config(input_yaml_path)
    self.assertTrue(is_expand_config_equal(dict1, dict2))


def is_expand_config_equal(config_a, config_b):

  def sort_by_project_id(proj):
    return proj['project_id']

  keys = set()
  for i in config_a:
    if i != utils.IMPORT_PATTERN_TAG and i != utils.IMPORT_FILES_TAG:
      if i in config_b:
        keys.add(i)
      else:
        return False

  for i in config_b:
    if i != utils.IMPORT_PATTERN_TAG and i != utils.IMPORT_FILES_TAG:
      if i in config_a:
        keys.add(i)
      else:
        return False

  for k in keys:
    if isinstance(config_a[k], list) and isinstance(config_b[k], list):
      config_a[k].sort(key=sort_by_project_id)
      config_b[k].sort(key=sort_by_project_id)
      if config_a[k] != config_b[k]:
        return False
    elif isinstance(config_a[k], dict) and isinstance(config_b[k], dict):
      if not is_expand_config_equal(config_a[k], config_b[k]):
        return False
    elif config_a[k] != config_b[k]:
      return False
  return True


if __name__ == '__main__':
  absltest.main()
