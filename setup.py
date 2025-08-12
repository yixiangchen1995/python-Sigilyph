'''
FilePath: /python-Sigilyph/setup.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2025-03-24 15:57:41
LastEditors: Yixiang Chen
LastEditTime: 2025-08-12 16:43:00
'''

from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Text Front for TTS'
#LONG_DESCRIPTION = 'Data Package for TTS with a slightly longer description'
LONG_DESCRIPTION = open("README.md", encoding="utf-8").read()

# 配置
setup(
        name="sigilyph", 
        version=VERSION,
        author="Yixiang Chen",
        author_email="<yixiangchen1995@gmail.com>",
        license='MIT',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url="https://github.com/yixiangchen1995/python-Sigilyph",
        packages=find_packages(),
        install_requires=[
            'g2p_en',
            'jieba',
            'jieba_fast',
            'pypinyin',
            'WeTextProcessing==1.0.3',
            'langid'
        ], # add any additional packages that ## add tinytag package
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.10',
        ]
)