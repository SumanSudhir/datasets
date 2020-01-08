# coding=utf-8
# Copyright 2019 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""SCAN tasks with various different splits."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow as tf
import tensorflow_datasets.public_api as tfds

_CITATION = """
@inproceedings{Lake2018GeneralizationWS,
  title={Generalization without Systematicity: On the Compositional Skills of
         Sequence-to-Sequence Recurrent Networks},
  author={Brenden M. Lake and Marco Baroni},
  booktitle={ICML},
  year={2018},
  url={https://arxiv.org/pdf/1711.00350.pdf},
}
"""

_DESCRIPTION = """SCAN tasks with various splits.

SCAN is a set of simple language-driven navigation tasks for studying
compositional learning and zero-shot generalization.

See https://github.com/brendenlake/SCAN for a description of the splits.

Example usage:
train_examples, test_examples = tfds.load('scan/length')
"""

_DATA_URL = 'https://github.com/brendenlake/SCAN/archive/master.zip'


class ScanConfig(tfds.core.BuilderConfig):
  """BuilderConfig for SCAN."""

  @tfds.core.disallow_positional_args
  def __init__(self, name, directory=None, **kwargs):
    """BuilderConfig for SCAN.

    Args:
      name: Unique name of the split.
      directory: Which subdirectory to read the split from.
      **kwargs: keyword arguments forwarded to super.
    """
    # Version history:
    super(ScanConfig, self).__init__(
        name=name,
        version=tfds.core.Version('1.0.0'),
        description=_DESCRIPTION,
        **kwargs)
    if directory is None:
      self.directory = name + '_split'
    else:
      self.directory = directory


_COMMANDS = 'commands'
_ACTIONS = 'actions'


class Scan(tfds.core.GeneratorBasedBuilder):
  """SCAN task / splits as proposed by Brenden M. Lake and Marco Baroni."""

  BUILDER_CONFIGS = [
      ScanConfig(name='simple'),
      ScanConfig(name='addprim_jump', directory='add_prim_split'),
      ScanConfig(name='addprim_turn_left', directory='add_prim_split'),
      ScanConfig(name='filler_num0', directory='filler_split'),
      ScanConfig(name='filler_num1', directory='filler_split'),
      ScanConfig(name='filler_num2', directory='filler_split'),
      ScanConfig(name='filler_num3', directory='filler_split'),
      ScanConfig(name='length'),
      ScanConfig(name='template_around_right', directory='template_split'),
      ScanConfig(name='template_jump_around_right', directory='template_split'),
      ScanConfig(name='template_opposite_right', directory='template_split'),
      ScanConfig(name='template_right', directory='template_split'),
  ]

  def _info(self):
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            _COMMANDS: tfds.features.Text(),
            _ACTIONS: tfds.features.Text(),
        }),
        supervised_keys=(_COMMANDS, _ACTIONS),
        homepage='https://github.com/brendenlake/SCAN',
        citation=_CITATION,
    )

  def _split_generators(self, dl_manager):
    """Returns SplitGenerators."""
    data_dir = dl_manager.download_and_extract(
        tfds.download.Resource(
            url=_DATA_URL,
            # Specify extract method manually as filename reported by github.com
            # misses the .zip extension so auto-detection doesn't work.
            extract_method=tfds.download.ExtractMethod.ZIP))
    data_dir = os.path.join(data_dir, 'SCAN-master',
                            self.builder_config.directory)
    split = self.builder_config.name
    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                'filepath':
                    os.path.join(data_dir, 'tasks_train_' + split + '.txt')
            }),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
                'filepath':
                    os.path.join(data_dir, 'tasks_test_' + split + '.txt')
            })
    ]

  def _generate_examples(self, filepath):
    """Yields examples."""
    with tf.io.gfile.GFile(filepath) as infile:
      for i, line in enumerate(infile):
        if not line.startswith('IN: '):
          continue
        # Chop the prefix and split string between input and output
        commands, actions = line[len('IN: '):].strip().split(' OUT: ', 1)
        yield i, {_COMMANDS: commands, _ACTIONS: actions}
