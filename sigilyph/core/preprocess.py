'''
FilePath: /python-Sigilyph/sigilyph/core/preprocess.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-05-13 11:01:26
LastEditors: Yixiang Chen
LastEditTime: 2025-05-14 20:26:27
'''

def replace_proper(text, namedict):
    for k,v in namedict.items():
        text = text.replace(k,v)
    return text


