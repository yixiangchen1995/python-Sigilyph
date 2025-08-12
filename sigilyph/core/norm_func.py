'''
FilePath: /python-Sigilyph/sigilyph/core/norm_func.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 17:50:26
LastEditors: Yixiang Chen
LastEditTime: 2025-08-12 15:42:55
'''


import re

from sigilyph.core.symbols import punctuation, punc_map_ch

from tn.chinese.normalizer import Normalizer as ZhNormalizer
from tn.english.normalizer import Normalizer as EnNormalizer

#zh_tn_model = ZhNormalizer(remove_erhua=False, full_to_half=False)
#en_tn_model = EnNormalizer()
zh_tn_model = ZhNormalizer(cache_dir='./sigilyph/core/cache_dir', remove_erhua=False, full_to_half=False)
en_tn_model = EnNormalizer(cache_dir='./sigilyph/core/cache_dir')

import json
#import sys
#sys.path.append('text_front')
#with open('./special_dict.json', 'r', encoding="utf-8") as infi:
#with open('./text_front/special_dict.json', 'r', encoding="utf-8") as infi:
with open('./sigilyph/core/special_dict.json', 'r', encoding="utf-8") as infi:
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

pre_replace_dict = {"AlphaFold-Plus": "AlphaFold Plus"}
def preprocess_first_old(text, use_lang='zh'):
    text = replace_with_dict(text, pre_replace_dict)
    norm_text = pro_norm(text, use_lang)
    print(norm_text)
    rep_text = replace_with_dict(norm_text, special_dict)
    return rep_text

def preprocess_first(text, before_replace_dict, special_word_dict, norm_use_lang='zh'):
    text = replace_with_dict(text, before_replace_dict)
    norm_text = pro_norm(text, norm_use_lang)
    print(norm_text)
    rep_text = replace_with_dict(norm_text, special_word_dict)
    return rep_text


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

def text_norm_cn(text):
    text = normalizer(text)
    text = replace_punc(text)
    return text

def text_norm_en(text):
    
    return text 