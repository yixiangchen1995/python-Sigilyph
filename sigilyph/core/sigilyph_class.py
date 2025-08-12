'''
FilePath: /python-Sigilyph/sigilyph/core/sigilyph_class.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-08-12 14:42:50
LastEditors: Yixiang Chen
LastEditTime: 2025-08-12 15:41:33
'''

import langid
import re
import json

import jieba
import jieba.posseg

from sigilyph.core.g2p_func import g2p_en, g2p_cn
from sigilyph.core.norm_func import preprocess_first, text_norm_en, text_norm_cn
from sigilyph.core.symbols import punctuation 
from sigilyph.core.predict import before_replace_dict, special_word_dict, special_phrase

norm_func_dict = {
    'en': text_norm_en,
    'zh': text_norm_cn
}

g2p_func_dict = {
    'en': g2p_en,
    'zh': g2p_cn
}

class Sigilyph:
    def __init__(self, before_dict_path=None, special_dict_path=None):
        self.sil1symbol='-'
        self.punctuation = punctuation

        self.before_replace_dict = before_replace_dict 
        if before_dict_path:
            with open(before_dict_path, 'r', encoding="utf-8") as obdp:
                extra_before_dict = json.load(obdp)
            self.before_replace_dict.update(extra_before_dict)

        self.special_word_dict = special_word_dict
        if special_dict_path:
            with open(special_dict_path, 'r', encoding="utf-8") as obdp:
                extra_special_dict = json.load(obdp)
            self.special_word_dict.update(extra_special_dict)
        
        self.special_phrase = special_phrase 
    
    def forward(self, text, lang):
        phones = self.text_process(text, lang)
        phones = self.replace_sil2label(phones)
        return phones

    def text_process(self, text, lang, spflag=True, use_lang='zh'):
        text = preprocess_first(text, self.before_replace_dict, special_word_dict, norm_use_lang='zh')

        multi_lang_text_list = self.text_split_lang(text, lang) 

        all_phone = []
        for text_split_dict in multi_lang_text_list:
            use_lang = text_split_dict['lang']
            use_text = text_split_dict['text_split']
            if use_lang == 'phone':
                phonelist = use_text.split()
                all_phone.extend(phonelist) 
            else:
                if use_lang not in norm_func_dict.keys():
                    use_lang = 'zh'
                use_text = self.text_norm(use_text, use_lang)
                phone_list = self.g2p(use_text, use_lang)
                #all_phone.append('sil')
                all_phone.append('sil_lang')
                all_phone.append('<sp>')
                all_phone.extend(phone_list)
        #all_phone = postprocess(all_phone)
        all_phone = self.postprocess_tts(all_phone)
        if not spflag:
            while '<sp>' in all_phone:
                all_phone.remove('<sp>')
        return all_phone

    ###############  split text in line with lang ##############
    def text_split_lang(self, text, lang):
        if lang == 'ZH' or lang == 'zh':
            multi_lang_text_list = [{'lang':'zh', 'text_split': text}]
        elif lang == 'en':
            multi_lang_text_list = [{'lang':'en', 'text_split': text}]
        else:
            pretext_split =  re.split("(\[.*?\])", text, re.I|re.M)
            multi_lang_text_list = []
            pretext_split = list(filter(None, pretext_split))
            for utext in pretext_split:
                if utext[0] != '[':
                    pattern = r'([a-zA-Z ,.\!\?]+|[\u4e00-\u9fa5 ，。,.\t \"\！\？\“\”\、]+)'
                    text_split = re.findall(pattern, utext)
                    print(text_split)
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

    ######## text norm #########
    def text_norm(self, text, lang):
        outtext = norm_func_dict[lang](text)
        return outtext

    ############ g2p ################
    def g2p(self, text, lang):
        phoneme_list = g2p_func_dict[lang](text)
        return phoneme_list
    
    ############# post process #############
    def postprocess_tts(self, phonelist):
        #outlist = ['sil', '<sp>']
        outlist = []
        print(phonelist)
        for idx in range(len(phonelist)):
            pm = phonelist[idx]
            if pm not in self.punctuation:
                outlist.append(pm)
            elif pm == self.sil1symbol:
                outlist.append('sil_1')
            else:
                #outlist.append('sil')
                outlist.append('sil_punc')
                #outlist.append('<sp>')
        #if outlist[-1] == 'sil': 
        #    outlist.append('<sp>')
        #elif outlist[-2] != 'sil':
        #    outlist.append('sil')
        #    outlist.append('<sp>')
        if phonelist[-2] not in self.punctuation and outlist[-1].split('_')[0] != 'sil':
            #outlist.append('sil')
            outlist.append('sil_end')
            outlist.append('<sp>')
        return outlist

    ########## replace silence token ###############
    def replace_sil2label(phones):
        #phones = ['sil_1' if xx == 'sil_lang' else xx for xx in phones]
        phones = ['' if xx == 'sil_lang' else xx for xx in phones]
        phones = ['sil_2' if xx == 'sil_punc' else xx for xx in phones]
        phones = ['sil_2' if xx == 'sil_end' else xx for xx in phones]
        phones = ['sil_1' if xx == 'sil' else xx for xx in phones]
        phones = list(filter(None, phones))
        #outphones = []
        outphones = ['sil_1']
        for ele in phones:
            if outphones == []:
                outphones.append(ele)
            else:
                if ele.split('_')[0] == 'sil' and outphones[-1].split('_')[0] == 'sil':
                    outphones[-1] = 'sil_2'
                    #outphones[-1] = 'sil_1'
                else:
                    outphones.append(ele)
        #if outphones[-1].split('_')[0] == 'sil':
        #    outphones = outphones[:-1]
        return outphones
    
    
    

