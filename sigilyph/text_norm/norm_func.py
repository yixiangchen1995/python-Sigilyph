'''
FilePath: /python-Sigilyph/sigilyph/text_norm/norm_func.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 17:50:26
LastEditors: Yixiang Chen
LastEditTime: 2026-01-26 14:22:38
'''


import re

from sigilyph.core.symbols import punctuation, punc_map_ch

from sigilyph.fst_tool.infer_normalizer import ZhNormalizer, EnNormalizer


import os
from importlib_resources import files
basedir = files('sigilyph')

zh_tn_model = ZhNormalizer(version_id='v2', cache_dir=os.path.join(basedir, 'text_norm', 'cache_dir'), remove_erhua=False, full_to_half=False)
en_tn_model = EnNormalizer(version_id='v2', cache_dir=os.path.join(basedir, 'text_norm', 'cache_dir'))

import json
with open(os.path.join(basedir, 'core', 'special_dict.json'), 'r', encoding="utf-8") as infi:
    special_dict = json.load(infi)

def pro_norm(text, use_lang='zh'):
    if use_lang == 'zh':
        norm_text = zh_tn_model.normalize(text)
        #print("zh ", norm_text)
    else:
        norm_text = en_tn_model.normalize(text)
        #print("en ", norm_text)
    return norm_text

def replace_with_dict(text, replace_dict):
    for old, new in replace_dict.items():
        text = text.replace(old, new)
    return text

def replace_with_dict_re(text, replace_dict):
    pattern = re.compile("|".join(re.escape(key) for key in replace_dict.keys()))
    return pattern.sub(lambda m: replace_dict[m.group(0)], text)

def replace_roman_1_to_10(text: str) -> str:
    """
    将字符串中的罗马数字符号 Ⅰ～Ⅹ 替换为中文数字 一～十。
    其余任何字符（包括乱码、英文 I/V/X 等）都保持不变。
    """
    roman_to_cn = {
        'Ⅰ': '一',
        'Ⅱ': '二',
        'Ⅲ': '三',
        'Ⅳ': '四',
        'Ⅴ': '五',
        'Ⅵ': '六',
        'Ⅶ': '七',
        'Ⅷ': '八',
        'Ⅸ': '九',
        'Ⅹ': '十',
    }
    # 逐字符扫描，能映射的就换成中文数字，不能映射的原样保留
    return ''.join(roman_to_cn.get(ch, ch) for ch in text)

pre_replace_dict = {"AlphaFold-Plus": "AlphaFold Plus"}
def preprocess_first_old(text, use_lang='zh'):
    text = replace_with_dict(text, pre_replace_dict)
    norm_text = pro_norm(text, use_lang)
    #print(norm_text)
    rep_text = replace_with_dict(norm_text, special_dict)
    return rep_text

def preprocess_first(text, before_replace_dict, special_word_dict, norm_use_lang='zh'):
    text = replace_with_dict(text, before_replace_dict)
    norm_text = pro_norm(text, norm_use_lang)
    #print(norm_text)
    #rep_text = replace_with_dict(norm_text, special_word_dict)
    return norm_text
def post_process(text , special_word_dict):
    rep_text = replace_with_dict(text, special_word_dict)
    return rep_text


def preprocess_first_for_norm(text, before_replace_dict, norm_use_lang='zh'):
    text = replace_roman_1_to_10(text)
    text = replace_with_dict(text, before_replace_dict)
    return text

def normalizer(text):
    return text

def replace_punc(text):
    #text = text.replace("嗯", "恩").replace("呣", "母")
    pattern = re.compile("|".join(re.escape(p) for p in punc_map_ch.keys()))
    replaced_text = pattern.sub(lambda x: punc_map_ch[x.group()], text)
    replaced_text = re.sub(
        r"[^\u4e00-\u9fa5" + "".join(punctuation) + r"]+", "", replaced_text
    )
    return replaced_text

def replace_punc_part(text: str) -> str:
    """
    将中文句号、逗号、分号、引号替换为英文符号：
    。 -> .
    ， -> ,
    ； -> ;
    “ -> "
    ” -> "
    『 -> "
    』 -> "
    「 -> "
    」 -> "
    『』、「」等都统一为英文双引号
    其他符号不动
    """
    # 建立映射表
    mapping = {
        '。': '.',
        '，': ',',
        '；': ';',
        '“': '"',
        '”': '"',
        '「': '"',
        '」': '"',
        '『': '"',
        '』': '"',
    }

    # 构造正则：匹配所有需要替换的中文标点
    pattern = re.compile(r'[。，“”；「」『』]')

    # 使用 re.sub 进行替换
    return pattern.sub(lambda m: mapping[m.group(0)], text)

'''
def text_norm_cn(text):
    text = normalizer(text)
    text = replace_punc(text)
    return text

def text_norm_en(text):
    return text 
'''

def text_norm_cn(text, replace_punc_flag=True):
    norm_text = zh_tn_model.normalize(text) 
    if replace_punc_flag:
        norm_text = replace_punc_part(norm_text)
    return norm_text

def text_norm_en(text, replace_punc_flag=True):
    norm_text = en_tn_model.normalize(text)
    return norm_text 