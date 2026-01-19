'''
FilePath: /python-Sigilyph/sigilyph/text_norm/norm_func.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 17:50:26
LastEditors: Yixiang Chen
LastEditTime: 2026-01-19 10:09:56
'''

import os
import json
import re
from importlib_resources import files
from sigilyph.core.symbols import punctuation, punc_map_ch
from sigilyph.fst_tool.infer_normalizer import ZhNormalizer, EnNormalizer

basedir = files('sigilyph')
zh_tn_model = ZhNormalizer(version_id='v2', cache_dir=os.path.join(basedir, 'text_norm', 'cache_dir'), remove_erhua=False, full_to_half=False)
en_tn_model = EnNormalizer(version_id='v2', cache_dir=os.path.join(basedir, 'text_norm', 'cache_dir'))

#with open(os.path.join(basedir, 'core', 'special_dict.json'), 'r', encoding="utf-8") as infi:
#    special_dict = json.load(infi)

def pro_norm(text, use_lang='zh'):
    """Normalize text based on the specified language."""
    if use_lang == 'zh':
        return zh_tn_model.normalize(text)
    return en_tn_model.normalize(text)

def replace_with_dict(text, replace_dict):
    """Replace occurrences of keys in text with their corresponding values from replace_dict."""
    for old, new in replace_dict.items():
        text = text.replace(old, new)
    return text

def replace_with_dict_re(text, replace_dict):
    """Replace occurrences of keys in text using regular expressions."""
    pattern = re.compile("|".join(re.escape(key) for key in replace_dict.keys()))
    return pattern.sub(lambda m: replace_dict[m.group(0)], text)

def preprocess_first(text, before_replace_dict, special_word_dict, norm_use_lang='zh'):
    """Preprocess text by replacing specified words and normalizing."""
    text = replace_with_dict(text, before_replace_dict)
    norm_text = pro_norm(text, norm_use_lang)
    return replace_with_dict(norm_text, special_word_dict)

def post_process(text, special_word_dict):
    """Post-process text by replacing special words."""
    return replace_with_dict(text, special_word_dict)

def preprocess_first_for_norm(text, before_replace_dict):
    """Preprocess text for normalization."""
    return replace_with_dict(text, before_replace_dict)

def normalizer(text):
    """Placeholder for a normalizer function."""
    return text

def replace_punc(text):
    """Replace Chinese punctuation with corresponding characters."""
    pattern = re.compile("|".join(re.escape(p) for p in punc_map_ch.keys()))
    replaced_text = pattern.sub(lambda x: punc_map_ch[x.group()], text)
    return re.sub(r"[^\u4e00-\u9fa5" + "".join(punctuation) + r"]+", "", replaced_text)

def replace_punc_part(text: str) -> str:
    """Replace specific Chinese punctuation with English punctuation."""
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
    pattern = re.compile(r'[。，“”；「」『』]')
    return pattern.sub(lambda m: mapping[m.group(0)], text)

def text_norm_cn(text):
    """Normalize Chinese text."""
    norm_text = zh_tn_model.normalize(text)
    return replace_punc_part(norm_text)

def text_norm_en(text):
    """Normalize English text."""
    return en_tn_model.normalize(text)
