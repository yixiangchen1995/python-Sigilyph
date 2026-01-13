'''
FilePath: /python-Sigilyph/sigilyph/core/sigilyph_norm.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2026-01-07 15:46:04
LastEditors: Yixiang Chen
LastEditTime: 2026-01-13 10:17:01
'''

import langid
import re
import jieba

from sigilyph.core.norm_func import preprocess_first_for_norm, text_norm_en, text_norm_cn
from sigilyph.core.predict import special_phrase

norm_func_dict = {
    'en': text_norm_en,
    'zh': text_norm_cn
}

class SigilyphNormalizer:
    def __init__(self, norm_use_dict) -> None:
        self.sil1symbol='-'
        self.special_phrase = special_phrase 

        self.before_replace_dict = norm_use_dict 

    def normalize(self, text, lang, norm_use_lang='zh'):
        text = preprocess_first_for_norm(text, self.before_replace_dict, norm_use_lang=norm_use_lang)
        multi_lang_text_list = self.text_split_lang(text, lang) 
        all_phone = []
        outtext = ''
        for text_split_dict in multi_lang_text_list:
            use_lang = text_split_dict['lang']
            use_text = text_split_dict['text_split']
            if use_lang not in norm_func_dict.keys():
                use_lang = 'zh'
            use_text = self.text_norm(use_text, use_lang)
            outtext += use_text 
        return outtext 
    
    ######## text norm #########
    def text_norm(self, text, lang):
        outtext = norm_func_dict[lang](text)
        return outtext

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
                    pattern = r'([a-zA-Z ,.\!\?]+|[\u4e00-\u9fa5 ，。,.\t \"\！\？\“\”\、]+)'
                    text_split = re.findall(pattern, utext)
                    #print(text_split)
                    for idx in range(len(text_split)):
                        tmpts = text_split[idx]
                        tmp_lang = langid.classify(tmpts)[0]
                        if len(tmpts)>20:
                            if not self.has_punc(tmpts[:-1]):
                                tmpts = self.add_pause(tmpts, 'p')
                            if not self.has_punc(tmpts[:-1]):
                                tmpts = self.add_pause(tmpts, 'v')   
                        if tmpts in self.special_phrase:
                            tmpts = tmpts+self.sil1symbol
                        if tmp_lang in ['zh', 'jp', 'ja']:
                            tmp_lang = 'zh'
                            tmpts = tmpts.replace(' ', self.sil1symbol)
                        else:
                            tmp_lang = 'en' 
                        if not tmpts.isspace():
                            multi_lang_text_list.append({'lang':tmp_lang, 'text_split': tmpts})
                else:
                    phones = utext[1:-1]
                    multi_lang_text_list.append({'lang':'phone', 'text_split': phones})
        return multi_lang_text_list

    ##########  add parse ###############
    def has_punc(self, text):
        for char in text:
            if char in [',', '.', '!', '?', '，','。','？','！', self.sil1symbol]:
                return True
        return False
    
    def add_pause(self, text, tf='v'):
        segment = jieba.posseg.cut(text.strip())
        wlist = []
        flist = []
        for x in segment:
            wlist.append(x.word)
            flist.append(x.flag)
        idx = self.search_ele_mid(flist, tf)
        if idx != len(flist)-1:
            wlist.insert(idx, self.sil1symbol)
        outtext = ''.join(wlist)
        return outtext
    
    def search_ele_mid(self, flaglist, tf = 'v'):
        nowidx = -1
        halflen = (len(flaglist))//2
        for gap in range(len(flaglist)-halflen):
            nowidx = halflen - gap
            if flaglist[nowidx]==tf:
                return nowidx
            nowidx = halflen + gap
            if flaglist[nowidx]==tf:
                return nowidx
        return nowidx
