'''
FilePath: /python-Sigilyph/sigilyph/core/norm_func.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 17:50:26
LastEditors: Yixiang Chen
LastEditTime: 2025-05-13 11:49:03
'''


import re

from sigilyph.core.symbols import punctuation, punc_map_ch

from tn.chinese.normalizer import Normalizer
tn_normalizer = Normalizer(remove_interjections=False, remove_erhua=False).normalize

def normalizer(text):
    text = tn_normalizer(text)
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