'''
FilePath: /python-Sigilyph/sigilyph/text_norm/sigilyph_norm.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2026-01-07 15:46:04
LastEditors: Yixiang Chen
LastEditTime: 2026-01-26 15:20:26
'''

import langid
import re
import jieba
import os

from sigilyph.text_norm.norm_func import preprocess_first_for_norm, text_norm_en, text_norm_cn
from sigilyph.core.predict import special_phrase

norm_func_dict = {
    'en': text_norm_en,
    'zh': text_norm_cn
}

import json
from importlib_resources import files
basedir = files('sigilyph')
with open(os.path.join(basedir, 'text_norm', 'dict_special_word_polyphone.json'), 'r', encoding="utf-8") as infi:
    dict_special_word_polyphone_json = json.load(infi)
    dict_special_word_polyphone = dict_special_word_polyphone_json['polyphone_config']
with open(os.path.join(basedir, 'text_norm', 'dict_special_word_base.json'), 'r', encoding="utf-8") as infib:
    dict_special_word_base_json = json.load(infib)
    dict_special_word_base = dict_special_word_base_json['base_config']

def is_float_strip(s: str) -> bool:
    s = s.strip()   # 只去掉首尾空白
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

class SigilyphNormalizer:
    def __init__(self, norm_use_dict) -> None:
        self.sil1symbol='-'
        self.special_phrase = special_phrase 

        self.base_replace_dict = dict_special_word_base
        #self.base_replace_dict.update(dict_special_word_polyphone)

        self.before_replace_dict = self.base_replace_dict
        self.before_replace_dict.update(norm_use_dict)
    
    def fix_replace_dict(self, new_before_replace_dict):
        self.before_replace_dict = self.base_replace_dict
        self.before_replace_dict.update(new_before_replace_dict)

    def normalize(self, text, lang, norm_use_lang='zh', replace_punc_flag=False):
        text = preprocess_first_for_norm(text, self.before_replace_dict, norm_use_lang=norm_use_lang)
        multi_lang_text_list = self.text_split_lang(text, lang) 
        all_phone = []
        outtext = ''
        for text_split_dict in multi_lang_text_list:
            use_lang = text_split_dict['lang']
            use_text = text_split_dict['text_split']
            if use_lang not in norm_func_dict.keys():
                use_lang = 'zh'
            use_text = self.text_norm(use_text, use_lang, replace_punc_flag)
            outtext += use_text 
        return outtext 
    
    ######## text norm #########
    def text_norm(self, text, lang, replace_punc_flag=False):
        outtext = norm_func_dict[lang](text, replace_punc_flag)
        return outtext
    
    def split_with_units(self, text, regex):
        # 中文数字（常见大写+小写口语化）
        CHINESE_NUM_CHARS = "零一二三四五六七八九十百千万亿两〇壹贰叁肆伍陆柒捌玖拾佰仟萬億"
        # 单位模式：可按需要继续扩展
        unit_pattern = re.compile(r'^(\s*)(km/h|km|m/s|m|s|g|h|kg|mm|cm)\b')
        
        pieces = re.findall(regex, text)
        merged = []

        for piece in pieces:
            if merged:
                m = unit_pattern.match(piece)
                if m:
                    # 前一块最后一个字符
                    last_char = merged[-1][-1]
                    # 条件：前一块以“汉字或阿拉伯数字或中文数字”结尾
                    if (
                        re.match(r'[\u4e00-\u9fff\u3400-\u4dbf0-9]', last_char)
                        or last_char in CHINESE_NUM_CHARS
                    ):
                        # 把单位并到前一块
                        merged[-1] += m.group(1) + m.group(2)
                        # 当前块剩余部分（若有）单独保留
                        rest = piece[m.end():]
                        if rest:
                            merged.append(rest)
                        continue

            merged.append(piece)

        return merged

    ###############  split text in line with lang ##############
    def text_split_lang(self, text, lang):
        if lang == 'ZH' or lang == 'zh':
            multi_lang_text_list = [{'lang':'zh', 'text_split': text}]
        elif lang == 'en':
            multi_lang_text_list = [{'lang':'en', 'text_split': text}]
        else:
            # Phoneme be judged
            pretext_split =  re.split("(\[.*?\])", text, re.I|re.M)
            multi_lang_text_list = []
            pretext_split = list(filter(None, pretext_split))
            for utext in pretext_split:
                if utext[0] != '[':
                    #pattern = r'([a-zA-Z ,.\!\?]+|[\u4e00-\u9fa5 ，。,.\t \"\！\？\“\”\、]+)'
                    #text_split = re.findall(pattern, utext)
                    pattern = r'''(
                        # ---------- 中文块 ----------
                        # 汉字 + 数字 + 日期时间符号 + 中/英逗号句号 + 常见中文标点 +
                        # 全角空格 + 半角空格 + ℃ + / + % + 单位字母 k,m,g,h（大小写都算）
                        [\u4e00-\u9fff\u3400-\u4dbf
                        0-9
                        \-:~_                      # 日期/时间里的 - 和 :
                        ，。！？：；、…“”‘’「」『』《》．【】（）\u3000
                        ,\.\<\>                       # 英文逗号、英文句号
                        \x20                     # 半角空格
                        /%                       # / 和 %
                        ℃
                        $£￡¥￥฿€₹₽CHFR$
                        ]+
                        |
                        # ---------- 英文块 ----------
                        # 字母 + 数字 + 英文标点 + 其它空白（制表符/换行等）
                        [a-zA-Z
                        ,\.!?;:'"\-\(\)\[\]/\\_@#\$%&\+\|\>\<
                        \t\r\n\f\v               # 其它空白（不含普通空格）
                        ]+
                        |
                        # ---------- 其它块 ----------
                        # 不属于上面两类的字符（emoji、特殊符号等）
                        [^a-zA-Z0-9
                        \u4e00-\u9fff\u3400-\u4dbf
                        ，。！？：；、…“”‘’「」『』《》．【】（）\u3000
                        \-:
                        ,\.
                        \x20\t\r\n\f\v
                        /%
                        ℃
                        ]+
                    )'''
                    regex = re.compile(pattern, re.VERBOSE)
                    #text_split = re.findall(regex, utext)
                    text_split = self.split_with_units(utext, regex)
                    for idx in range(len(text_split)):
                        tmpts = text_split[idx]
                        #if tmpts.strip().isdigit():
                        if is_float_strip(tmpts):
                            tmp_lang = 'zh'
                        else:
                            tmp_lang = langid.classify(tmpts)[0]
                        if tmp_lang in ['zh', 'jp', 'ja']:
                            tmp_lang = 'zh'
                            #tmpts = tmpts.replace(' ', self.sil1symbol)
                        else:
                            tmp_lang = 'en' 
                        multi_lang_text_list.append({'lang':tmp_lang, 'text_split': tmpts})
                else:
                    phones = utext[1:-1]
                    multi_lang_text_list.append({'lang':'phone', 'text_split': phones})
        return multi_lang_text_list

