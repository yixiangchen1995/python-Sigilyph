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

from tn.processor import Processor
from tn.utils import get_abs_path

from pynini import accep, cross, string_file
from pynini.lib.pynutil import add_weight, delete, insert

# 配置电话中的连字符 '-' 如何发音：
# 'delete' -> 不发音（默认）；'gang' -> 读作 '杠'
PHONE_HYPHEN_MODE = 'delete'

# 配置哪些前文关键字后面的连续数字需要按电话读法读出。
# 后续只需往这个列表里添加新的关键字即可。
PHONE_PREFIXES = [
    '工号',
    '浮光掠影',
]


class Cardinal(Processor):

    def __init__(self):
        super().__init__('cardinal')
        self.number = None
        self.digits = None
        self.build_tagger()
        self.build_verbalizer()

    def build_tagger(self):
        zero = string_file(get_abs_path('chinese/data/number/zero.tsv'))
        digit = string_file(get_abs_path('chinese/data/number/digit.tsv'))
        teen = string_file(get_abs_path('chinese/data/number/teen.tsv'))
        sign = string_file(get_abs_path('chinese/data/number/sign.tsv'))
        dot = string_file(get_abs_path('chinese/data/number/dot.tsv'))

        rmzero = delete('0') | delete('０')
        rmpunct = delete(',').ques
        digits = zero | digit
        self.digits = digits

        # 11 => 十一
        ten = teen + insert('十') + (digit | rmzero)
        # 11 => 一十一
        tens = digit + insert('十') + (digit | rmzero)
        # 111, 101, 100
        hundred = (digit + insert('百') + (tens | (zero + digit) | rmzero**2))
        # 1111, 1011, 1001, 1000
        thousand = (digit + insert('千') + rmpunct + (hundred
                                                     | (zero + tens)
                                                     | (rmzero + zero + digit)
                                                     | rmzero**3))
        # 10001111, 1001111, 101111, 11111, 10111, 10011, 10001, 10000
        ten_thousand = ((thousand | hundred | ten | digit) + insert('万') +
                        (thousand
                         | (zero + rmpunct + hundred)
                         | (rmzero + rmpunct + zero + tens)
                         | (rmzero + rmpunct + rmzero + zero + digit)
                         | rmzero**4))

        # 1.11, 1.01
        number = digits | ten | hundred | thousand | ten_thousand
        number = sign.ques + number + (dot + digits.plus).ques
        number @= self.build_rule(
            cross('二百', '两百')
            | cross('二千', '两千')
            | cross('二万', '两万')).optimize()
        percent = insert('百分之') + number + delete('%')
        self.number = accep('约').ques + accep('人均').ques + (number | percent)

        # cardinal string like 127.0.0.1, used in ID, IP, etc.
        cardinal = digits.plus + (dot + digits.plus)**3
        cardinal |= percent
        # xxxx-xxx-xxx
        cardinal |= digits.plus + (delete('-') + digits.plus)**2
        # xxx-xxxxxxxx
        cardinal |= digits**3 + delete('-') + digits**8

        # phone numbers: every digit is read separately, and '1' is read as '幺'
        phone_digits = digits @ self.build_rule(cross('一', '幺'))
        if PHONE_HYPHEN_MODE == 'gang':
            phone_hyphen = cross('-', '杠')
        else:
            phone_hyphen = delete('-')
        phone_space = delete(' ')
        phone_sep = phone_hyphen | phone_space

        # three or five or eleven digit phone numbers
        phone = phone_digits**3 | phone_digits**5 | phone_digits**11
        # xxx-xxxx-xxxx or xxx xxxx xxxx (mobile phone)
        phone |= (phone_digits**3 + phone_sep + phone_digits**4 + phone_sep +
                  phone_digits**4)
        # 400/800 hotline: 4001234567 or 8001234567 (10 digits)
        phone |= (((accep('400') | accep('800')) @ phone_digits**3) +
                  phone_digits**7)
        # 400-xxx-xxxx or 800-xxx-xxx
        phone |= (((accep('400') | accep('800')) @ phone_digits**3) +
                  phone_hyphen + phone_digits**3 + phone_hyphen +
                  phone_digits**4)
        # landline with area code: 0xx(x)-xxxx(xxxx), e.g. 010-12345678,
        # 0755-12345678
        phone |= ((accep('0') @ phone_digits) + phone_digits**2 +
                  phone_digits.ques + phone_hyphen + phone_digits**7 +
                  phone_digits.ques)

        # bank card: 16-19 continuous digits, or xxxx-xxxx-xxxx-xxx /
        # xxxx xxxx xxxx xxx style
        bank_card = (phone_digits**16 | phone_digits**17 | phone_digits**18 |
                     phone_digits**19)
        bank_card |= (phone_digits**4 + phone_sep + phone_digits**4 +
                      phone_sep + phone_digits**4 + phone_sep +
                      (phone_digits**4 | phone_digits**5 | phone_digits**6 |
                       phone_digits**7))
        phone |= bank_card

        # email prefix: digits before '@' read as phone digits
        phone |= phone_digits.plus + accep('@')

        # digits following configured prefixes read as phone digits
        for prefix in PHONE_PREFIXES:
            phone |= accep(prefix) + delete(' ').ques + phone_digits.plus

        # mixed alphanumeric codes (order IDs, etc.): digits and uppercase
        # letters mixed together; digits are read digit-by-digit like phone
        # numbers, uppercase letters are kept as-is.
        alnum = phone_digits | self.UPPER
        mixed_code = ((alnum.star + phone_digits + alnum.star + self.UPPER +
                       alnum.star) |
                      (alnum.star + self.UPPER + alnum.star + phone_digits +
                       alnum.star))
        phone |= mixed_code

        # ID card: 15 or 18 continuous digits; or 17 digits + X/x
        id_card = phone_digits**15 | phone_digits**18
        id_card |= phone_digits**17 + (cross('X', '叉') | cross('x', '叉'))
        # Give ID card slightly higher priority than bank card so that 18-digit
        # numbers are treated as ID card rather than bank card.
        phone |= add_weight(id_card, -0.1)

        phone |= accep("尾号") + (accep("是") | accep("为")).ques + phone_digits**4
        cardinal |= add_weight(phone, -1.0)

        tagger = insert('value: "') + cardinal + insert('"')
        self.tagger = self.add_tokens(tagger)
