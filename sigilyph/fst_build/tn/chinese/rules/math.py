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

from tn.chinese.rules.cardinal import Cardinal
from tn.processor import Processor
from tn.utils import get_abs_path

from pynini import cross, string_file
from pynini.lib.pynutil import delete, insert, add_weight


class Math(Processor):

    def __init__(self):
        super().__init__(name="math")
        self.build_tagger()
        self.build_verbalizer()

    def build_tagger(self):
        operator = string_file(get_abs_path("chinese/data/math/operator.tsv"))
        # When it appears alone, it is treated as punctuation
        symbols = (cross("~", "到")
                   | cross(":", "比")
                   | cross("<", "小于")
                   | cross(">", "大于"))

        number = Cardinal().number
        math_start = (operator | symbols) + delete(" ").ques + number
        tagger = add_weight((number +
                  (delete(" ").ques +
                   (operator | symbols) + delete(" ").ques + number).star)
                  | math_start, 1)

        #pp = add_weight((number + cross('-', ',')).closure(4), 0.1)
        pp = add_weight(number +
                  (delete(" ").ques +
                   cross('-', '<sil>') + delete(" ").ques + number).closure(4), 0.1)
        fixcase = pp

        tmpadd = add_weight(number + delete(" ").ques + cross("'", "分钟") + number + delete(" ").ques + cross("''", "秒"), 0.1)
        tmpsec = number + cross("sec", "秒")
        tmpadd |= tmpsec 

        digits = Cardinal().digits
        phone_head = add_weight(cross('（', '') + cross('+', '')+ digits**2 + cross('）', '<sil>'), 0.1)
        tmpadd |= phone_head
        dash_rm = add_weight(cross('--《', '<sil>《'), 0.1)
        tmpadd |= dash_rm

        # standalone symbols should not override fallback hyphen-to-到 in general text
        # standalone operators are only handled as part of numeric/math expressions.
        tagger = insert('value: "') + (tagger | fixcase | tmpadd) + insert('"')
        self.tagger = self.add_tokens(tagger)
