'''
FilePath: /python-Sigilyph/sigilyph/core/g2p_func.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-31 16:55:51
LastEditors: Yixiang Chen
LastEditTime: 2025-08-12 14:42:02
'''

from g2p_en import G2p
_g2p_en = G2p()

def g2p_en(text, sp_sign='<sp>'):
    phone_list = _g2p_en(text)
    phone_list = [sp_sign if xx == " " else xx for xx in phone_list]
    if len(phone_list)>1 and phone_list[-1] != sp_sign:
        phone_list.append(sp_sign) 
    return phone_list


from pypinyin import lazy_pinyin, Style

from sigilyph.core.symbols import punctuation, punc_map_ch, cn_word2phone_dict
for punc in punctuation:
    cn_word2phone_dict[punc] = punc

def g2p_cn(text):
    pinyinlist = lazy_pinyin(text, style=Style.TONE3, neutral_tone_with_five=True, tone_sandhi=True)
    outlist = []
    for pp in pinyinlist:
        if pp in cn_word2phone_dict.keys():
            outlist.extend(cn_word2phone_dict[pp])
            outlist.append('<sp>')
        else:
            for ch in pp:
                outlist.extend(cn_word2phone_dict[ch]) 
                outlist.append('<sp>')
    if len(outlist) > 4:
        if outlist[-2] == 'sil' and outlist[-4] == 'sil':
            outlist = outlist[:-2]
    return outlist





