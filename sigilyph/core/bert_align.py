'''
FilePath: /python-Sigilyph/sigilyph/core/bert_align.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-09-24 15:13:38
LastEditors: Yixiang Chen
LastEditTime: 2025-09-28 11:05:20
'''

import torch
from transformers import BertTokenizer, BertModel

import langid
from g2p_en import G2p
_g2p_en = G2p()

from pypinyin import lazy_pinyin, Style

from sigilyph.core.norm_func import text_norm_cn
from sigilyph.core.symbols import punctuation, punc_map_ch, cn_word2phone_dict
for punc in punctuation:
    cn_word2phone_dict[punc] = punc

def _g2p_cn(text):
    pinyinlist = lazy_pinyin(text, style=Style.TONE3, neutral_tone_with_five=True, tone_sandhi=True)
    outlist = []
    for pp in pinyinlist:
        if pp in cn_word2phone_dict.keys():
            outlist.extend(cn_word2phone_dict[pp])
        else:
            for ch in pp:
                if ch in cn_word2phone_dict.keys():
                    outlist.extend(cn_word2phone_dict[ch]) 
                else:
                    outlist.extend('sil')
    return outlist 

def g2p_word(word):
    tmp_lang = langid.classify(word)[0]
    if tmp_lang in ['zh', 'jp', 'ja']:
        tmp_lang = 'zh'
    else:
        tmp_lang = 'en' 
    if tmp_lang == 'zh':
        return _g2p_cn(word) 
    else:
        return _g2p_en(word) 

class AlignBert():
    def __init__(self, tkn_cache_dir, vocab_file):
        
        #tkn_cache_dir = "./tmp/"
        self.vocab_dict = self.load_vocab(vocab_file) 
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', cache_dir=tkn_cache_dir)
        self.g2p_word = g2p_word 
        self.symbol_list = ['[CLS]', '[SEP]', '?', '!', '.', ',', '，', '。']

        self.empty_bert = torch.zeros([768])

    def gen_seqbert(self, mfa_phones, text, bert):
        norm_text = text_norm_cn(text)
        midph_list, midph2bertid_dict = self.get_midph(norm_text)
        phoneme2midph_dict = self.get_phoneme2midph_dict(mfa_phones, midph_list)
        phoneme2bertid_dict = self.get_phoneme2bertid_dict(midph2bertid_dict, phoneme2midph_dict)
        seqbert = []
        for idx in range(len(phoneme2bertid_dict)):
            bertid = phoneme2bertid_dict[idx]
            if bertid >=0:
                seqbert.append(bert[bertid])
            else:
                seqbert.append(self.empty_bert)
        seqbert = torch.stack(seqbert)
        return seqbert 

    def load_vocab(self, vocab_file):
        vocab_dict = {}
        with open(vocab_file, 'r') as ovf:
            lines = ovf.readlines()
        for idx in range(len(lines)):
            line = lines[idx]
            tt = line.strip()
            vocab_dict[idx] = tt
        del lines
        return vocab_dict

    def id2text(self, idlist):
        outlist = []
        for idx in range(len(idlist)):
            outlist.append(self.vocab_dict[int(idlist[idx])])
        return outlist
        
    def get_midph(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        ret = self.id2text(encoded_input['input_ids'][0])
        wordph_list = []
        for word in ret[1:-1]:
            word_phoneme = self.g2p_word(word)
            wordph_list.append(word_phoneme)
        midph_list = []
        midph2bertid_dict = {}
        midph_list.append(ret[0])
        midph2bertid_dict[0] = 0
        for widx in range(len(wordph_list)):
            for phidx in range(len(wordph_list[widx])):
                phoneme = wordph_list[widx][phidx]
                midph_list.append(phoneme)
                midph2bertid_dict[len(midph_list)-1]=widx+1
        midph_list.append(ret[-1])
        midph2bertid_dict[len(midph_list)-1] = len(ret)-1
        return midph_list, midph2bertid_dict
    
    def get_phoneme2midph_dict(self, mfa_phones, midph_list):
        fixed_midph_list = []
        for idx in range(len(midph_list)):
            if midph_list[idx] in self.symbol_list:
                fixed_midph_list.append('sil')
            else:
                fixed_midph_list.append(midph_list[idx])
        phoneme2midph_dict = self.lcs(mfa_phones, fixed_midph_list)
        return phoneme2midph_dict

    def lcs(self, mfa_phones, midph_list):
        n, m = len(midph_list), len(mfa_phones)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        phoneme2midph_dict = {}
        for idx in range(1, m+1):
            phoneme2midph_dict[idx-1]=-1
        
        for idx in range(1, m+1):
            for midph_id in range(1, n+1):
                curr_ph = mfa_phones[idx-1]
                if curr_ph == midph_list[midph_id-1]:
                    dp[idx][midph_id] = dp[idx-1][midph_id-1] + 1
                else:
                    dp[idx][midph_id] = max(dp[idx-1][midph_id], dp[idx][midph_id-1])
        n, m = len(midph_list), len(mfa_phones)
        while m > 0 and n > 0:
            if mfa_phones[m-1] == midph_list[n-1] and dp[m][n] == dp[m-1][n-1] + 1:
                phoneme2midph_dict[m-1] = n-1
                m, n = m-1, n-1
                continue
            if dp[m][n] == dp[m-1][n]:
                m, n = m-1, n
                continue
            if dp[m][n] == dp[m][n-1]:
                m, n = m, n-1
                continue
        return phoneme2midph_dict    


    def get_phoneme2bertid_dict(self, midph2bertid_dict, phoneme2midph_dict):
        phoneme2bertid_dict = {}
        for idx in range(len(phoneme2midph_dict)):
            phoneme_id = idx
            midph_id = phoneme2midph_dict[phoneme_id] 
            #if midph_id not in midph2bertid_dict.keys():
            if midph_id == -1:
                phoneme2bertid_dict[idx] = -1
            else:
                phoneme2bertid_dict[idx] = midph2bertid_dict[midph_id]
        return phoneme2bertid_dict 
