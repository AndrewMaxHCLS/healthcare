"""Independent tool to split projects in a yaml file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from absl import app
from absl import flags
from deploy.utils import utils

FLAGS = flags.FLAGS

flags.DEFINE_string('project_yaml', None,
                    'Location of the project config YAML.')
flags.DEFINE_string('output_overall_yaml', None,
                    'Location of the project config YAML.')


def split_into_different_files(input_yaml_path, output_overall_path):
  """Split projects into separate files."""
  input_yaml_path = utils.normalize_path(input_yaml_path)
  overall = utils.load_config(input_yaml_path)
  newoverall = overall.copy()
  newoverall.pop('projects')
  newoverall[utils.IMPORT_PATTERN_TAG] = ['./*.yaml']
  utils.write_yaml_file(newoverall, output_overall_path)

  for proj in overall.get('projects', []):
    dict_proj = {'projects': [proj]}
    utils.write_yaml_file(
        dict_proj,
        os.path.join(
            os.path.dirname(output_overall_path), proj['project_id'] + '.yaml'))


def main(argv):
  del argv  # Unused.
  output_overall_path = FLAGS.project_yaml
  if FLAGS.output_overall_yaml:
    output_overall_path = FLAGS.output_overall_yaml
  split_into_different_files(FLAGS.project_yaml, output_overall_path)


if __name__ == '__main__':
  flags.mark_flag_as_required('project_yaml')
  app.run(main)
