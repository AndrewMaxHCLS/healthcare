"""Tests for deploy.other_tools.project_splitter."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tempfile

from absl import flags
from absl.testing import absltest
from deploy.other_tools import project_splitter
from deploy.utils import utils

FLAGS = flags.FLAGS


class ProjectSplitterTest(absltest.TestCase):

  def test_combine_split_projects(self):
    FLAGS.dry_run = False
    with tempfile.TemporaryDirectory() as tmp_dir:
      output_overall_yaml = os.path.join(tmp_dir, 'new.yaml')
      input_yaml = 'deploy/samples/project_with_remote_audit_logs.yaml'
      project_splitter.split_into_different_files(input_yaml,
                                                  output_overall_yaml)
      root_config_new = utils.load_config(output_overall_yaml)
      root_config_old = utils.load_config(utils.normalize_path(input_yaml))

      def sort_by_project_id(proj):
        return proj['project_id']

      root_config_old['projects'].sort(key=sort_by_project_id)
      root_config_new['projects'].sort(key=sort_by_project_id)
      for i in root_config_old:
        self.assertEqual(root_config_new[i], root_config_old[i])
      for i in root_config_new:
        if i == utils.IMPORT_PATTERN_TAG:
          continue
        self.assertEqual(root_config_new[i], root_config_old[i])


if __name__ == '__main__':
  absltest.main()
