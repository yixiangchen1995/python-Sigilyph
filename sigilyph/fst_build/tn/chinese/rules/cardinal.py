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

import string

from pynini import accep, cross, string_file, union
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

# 配置邮箱地址中哪些后缀形式保持原样（不转换为大写加空格）。
# 这里应同时包含原始后缀以及前置替换后的别名形式（如 '点com'）。
# 其他后缀的字母会按大写加空格处理。
EMAIL_RESERVED_SUFFIXES = [
    '.com',
    '点com',
    '.cn',
    '点cn',
    '.net',
    '点net',
]

# 配置邮箱 local 部分中下划线可能被前置替换成的形式。
# 这些形式会在邮箱上下文中原样保留，不会还原为 '_'。
EMAIL_UNDERSCORE_ALIASES = [
    ' 下划线 ',
    '下划线',
    ' Underscore ',
    'Underscore',
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

        # 邮箱规则：local 和 domain 中的英文字母转换成大写加空格，
        # 保留后缀（EMAIL_RESERVED_SUFFIXES）保持原样，其他后缀同样转换。
        alpha_to_upper_space = union(*[
            cross(c, c.upper() + ' ') for c in string.ascii_letters
        ])
        # 下划线别名（前置替换可能把 '_' 变成其他文本，这里原样保留）
        underscore_alias = union(*[
            accep(alias) for alias in EMAIL_UNDERSCORE_ALIASES
        ])
        # local 部分允许字母、数字、下划线原始形式及其别名、-、.
        email_local_char = (alpha_to_upper_space | phone_digits | accep('_')
                            | underscore_alias | accep('-') | accep('.'))
        # domain label 允许字母、数字及连字符 -
        email_domain_char = alpha_to_upper_space | phone_digits | accep('-')
        email_domain_label = email_domain_char.plus
        reserved_suffix = add_weight(
            union(*[accep(suffix) for suffix in EMAIL_RESERVED_SUFFIXES]),
            -0.1)
        other_suffix = accep('.') + alpha_to_upper_space.plus
        email = (email_local_char.plus + accep('@') +
                 (email_domain_label +
                  (accep('.') + email_domain_label).star +
                  (reserved_suffix | other_suffix)))
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
        # xxx-xxx-xxxx or xxx xxx xxxx, hyphen or space separated
        phone |= (phone_digits**3 + phone_sep + phone_digits**3 + phone_sep +
                  phone_digits**4)
        # xxx-xxx or xxx xxx (short code fragments), hyphen or space separated
        phone |= (phone_digits**3 + phone_sep + phone_digits**3)
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

        # email: letters to uppercase+space, reserved suffixes kept as-is
        phone |= email

        # 【】bracketed account: letters to uppercase+space, digits read as phone digits
        bracket_content_char = alpha_to_upper_space | phone_digits
        bracket_account = (accep('【') + bracket_content_char.plus +
                           accep('】'))
        phone |= bracket_account

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
