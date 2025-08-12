'''
FilePath: /python-Sigilyph/sigilyph/core/text_process.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 16:31:26
LastEditors: Yixiang Chen
LastEditTime: 2025-08-12 14:40:42
'''


import langid
import re

import jieba
import jieba.posseg

from sigilyph.core.g2p_func import g2p_en, g2p_cn
from sigilyph.core.norm_func import preprocess_first, text_norm_en, text_norm_cn

from sigilyph.core.symbols import base_phone_set, cn_phone_set, en_phone_set, punctuation, special_phrase

#all_phone_set = [] + sorted(set(base_phone_set + cn_phone_set + en_phone_set))
#all_phone_set = [] + list(set(base_phone_set)) + list(set(cn_phone_set + en_phone_set))
all_phone_set = [] + sorted(set(base_phone_set)) + sorted(set(cn_phone_set)) + sorted(set(en_phone_set))
all_phone_dict = {xx:idx for idx, xx in enumerate(all_phone_set)}

norm_func_dict = {
    'en': text_norm_en,
    'zh': text_norm_cn
}

g2p_func_dict = {
    'en': g2p_en,
    'zh': g2p_cn
}

sil1symbol='-'

def text_split_lang_old(text, lang):
    if lang == 'ZH' or lang == 'zh':
        multi_lang_text_list = [{'lang':'zh', 'text_split': text}]
    elif lang == 'en':
        multi_lang_text_list = [{'lang':'en', 'text_split': text}]
    else:
        pattern = r'([a-zA-Z ,.\!\?\"]+|[\u4e00-\u9fa5 ，。\！\？\“\”]+)'
        text_split = re.findall(pattern, text)
        multi_lang_text_list = []
        for idx in range(len(text_split)):
            tmpts = text_split[idx]
            tmp_lang = langid.classify(tmpts)[0]
            multi_lang_text_list.append({'lang':tmp_lang, 'text_split': tmpts})
    return multi_lang_text_list

def text_split_lang_bk0724(text, lang):
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
                pattern = r'([a-zA-Z ,.\!\?\"]+|[\u4e00-\u9fa5 ，。,.\t \！\？]+)'
                text_split = re.findall(pattern, utext)
                for idx in range(len(text_split)):
                    tmpts = text_split[idx]
                    tmp_lang = langid.classify(tmpts)[0]
                    if tmp_lang in ['zh', 'jp', 'ja']:
                        tmp_lang = 'zh'
                    else:
                        tmp_lang = 'en' 
                    if not tmpts.isspace():
                        multi_lang_text_list.append({'lang':tmp_lang, 'text_split': tmpts})
            else:
                phones = utext[1:-1]
                multi_lang_text_list.append({'lang':'phone', 'text_split': phones})
    return multi_lang_text_list


def search_ele_mid(flaglist, tf = 'v'):
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

def add_pause(text, tf='v'):
    segment = jieba.posseg.cut(text.strip())
    wlist = []
    flist = []
    for x in segment:
        wlist.append(x.word)
        flist.append(x.flag)
    idx = search_ele_mid(flist, tf)
    if idx != len(flist)-1:
        wlist.insert(idx, sil1symbol)
    outtext = ''.join(wlist)
    return outtext

def has_punc(text):
    for char in text:
        if char in [',', '.', '!', '?', '，','。','？','！', sil1symbol]:
            return True
    return False

def text_split_lang(text, lang):
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
                        if not has_punc(tmpts[:-1]):
                            tmpts = add_pause(tmpts, 'p')
                        if not has_punc(tmpts[:-1]):
                            tmpts = add_pause(tmpts, 'v')   
                    if tmpts in special_phrase:
                        tmpts = tmpts+sil1symbol
                    if tmp_lang in ['zh', 'jp', 'ja']:
                        tmp_lang = 'zh'
                        tmpts = tmpts.replace(' ', sil1symbol)
                    else:
                        tmp_lang = 'en' 
                    if not tmpts.isspace():
                        multi_lang_text_list.append({'lang':tmp_lang, 'text_split': tmpts})
            else:
                phones = utext[1:-1]
                multi_lang_text_list.append({'lang':'phone', 'text_split': phones})
    return multi_lang_text_list

def text_norm(text, lang):
    outtext = norm_func_dict[lang](text)
    return outtext

def g2p(text, lang):
    phoneme_list = g2p_func_dict[lang](text)
    return phoneme_list

def tokenizer(phoneme_list):
    #token_list = [all_phone_dict[pho] for pho in phoneme_list]
    token_list = [all_phone_dict[pho] if pho in all_phone_dict.keys() else all_phone_dict['sil'] for pho in phoneme_list]
    return token_list 

def postprocess(phonelist):
    outlist = [xx if xx not in punctuation else 'sil' for xx in phonelist]
    return outlist

def postprocess_tts(phonelist):
    #outlist = ['sil', '<sp>']
    outlist = []
    print(phonelist)
    for idx in range(len(phonelist)):
        pm = phonelist[idx]
        if pm not in punctuation:
            outlist.append(pm)
        elif pm == sil1symbol:
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
    if phonelist[-2] not in punctuation and outlist[-1].split('_')[0] != 'sil':
        #outlist.append('sil')
        outlist.append('sil_end')
        outlist.append('<sp>')
    return outlist

def text_process_old(text, lang, spflag=True):
    multi_lang_text_list = text_split_lang(text, lang) 

    all_phone = []
    for text_split_dict in multi_lang_text_list:
        use_lang = text_split_dict['lang']
        if use_lang not in norm_func_dict.keys():
            use_lang = 'zh'
        use_text = text_split_dict['text_split']
        use_text = text_norm(use_text, use_lang) 
        phone_list = g2p(use_text, use_lang)
        #all_phone.append('sil')
        all_phone.append('sil_lang')
        all_phone.append('<sp>')
        all_phone.extend(phone_list)
    #all_phone = postprocess(all_phone)
    all_phone = postprocess_tts(all_phone)
    if not spflag:
        while '<sp>' in all_phone:
            all_phone.remove('<sp>')
    return all_phone

def text_process(text, lang, spflag=True, use_lang='zh'):
    text = preprocess_first(text, use_lang=use_lang)

    multi_lang_text_list = text_split_lang(text, lang) 

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
            use_text = text_norm(use_text, use_lang)
            phone_list = g2p(use_text, use_lang)
            #all_phone.append('sil')
            all_phone.append('sil_lang')
            all_phone.append('<sp>')
            all_phone.extend(phone_list)
    #all_phone = postprocess(all_phone)
    all_phone = postprocess_tts(all_phone)
    if not spflag:
        while '<sp>' in all_phone:
            all_phone.remove('<sp>')
    return all_phone

def replace_sil2label_old(phones):
    phones = ['sil_1' if xx == 'sil_lang' else xx for xx in phones]
    phones = ['sil_2' if xx == 'sil_punc' else xx for xx in phones]
    phones = ['sil_2' if xx == 'sil_end' else xx for xx in phones]
    phones = ['sil_1' if xx == 'sil' else xx for xx in phones]
    outphones = []
    for ele in phones:
        if outphones == []:
            outphones.append(ele)
        else:
            if ele.split('_')[0] == 'sil' and outphones[-1].split('_')[0] == 'sil':
                #outphones[-1] = 'sil_2'
                outphones[-1] = 'sil_1'
            else:
                outphones.append(ele)
    if outphones[-1].split('_')[0] == 'sil':
        outphones = outphones[:-1]
    return outphones

def replace_sil2label_0808(phones):
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
                #outphones[-1] = 'sil_2'
                outphones[-1] = 'sil_1'
            else:
                outphones.append(ele)
    if outphones[-1].split('_')[0] == 'sil':
        outphones = outphones[:-1]
    return outphones

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


def text_process_asr(text, lang):
    multi_lang_text_list = text_split_lang(text, lang) 

    all_phone = []
    for text_split_dict in multi_lang_text_list:
        use_lang = text_split_dict['lang']
        use_text = text_split_dict['text_split']
        use_text = text_norm(use_text, use_lang) 
        phone_list = g2p(use_text, use_lang)
        phone_list_new = []
        for idx in range(len(phone_list)):
            tmpp = phone_list[idx]
            if tmpp != '<sp>':
                phone_list_new.append(tmpp)
        all_phone.extend(phone_list_new)
    all_phone = postprocess(all_phone)
    if all_phone[0] != 'sil':
        all_phone = ['sil'] + all_phone 
    if all_phone[-1] != 'sil': 
        all_phone = all_phone + ['sil']
    
    return all_phone