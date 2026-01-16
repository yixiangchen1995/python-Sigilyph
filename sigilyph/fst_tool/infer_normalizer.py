# Copyright (c) 2022 Zhendong Peng (pzd17@tsinghua.org.cn)
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

from sigilyph.fst_tool.processor import Processor
from importlib_resources import files

class ZhNormalizer(Processor):

    def __init__(self,
                 version_id='v1',
                 cache_dir=None,
                 overwrite_cache=False,
                 remove_interjections=True,
                 remove_erhua=True,
                 traditional_to_simple=True,
                 remove_puncts=False,
                 full_to_half=True,
                 tag_oov=False):
        super().__init__(name='zh_normalizer')
        self.remove_interjections = remove_interjections
        self.remove_erhua = remove_erhua
        self.traditional_to_simple = traditional_to_simple
        self.remove_puncts = remove_puncts
        self.full_to_half = full_to_half
        self.tag_oov = tag_oov
        if cache_dir is None:
            cache_dir = files("no_fst")
        #self.build_fst('zh_tn', cache_dir, overwrite_cache)
        self.build_fst('textnorm_zh_' + version_id, cache_dir, overwrite_cache)


class EnNormalizer(Processor):
    def __init__(self, version_id='v1', cache_dir=None, overwrite_cache=False):
        super().__init__(name='en_normalizer', ordertype="en_tn")
        if cache_dir is None:
            cache_dir = files("no_fst")
        #self.build_fst('en_tn', cache_dir, overwrite_cache)
        self.build_fst('textnorm_en_' + version_id, cache_dir, overwrite_cache)