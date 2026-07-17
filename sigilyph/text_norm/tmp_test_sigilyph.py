import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from sigilyph.text_norm.sigilyph_norm import SigilyphNormalizer

json_path = os.path.join(os.path.dirname(__file__), 'custom_replace_dict.json')
with open(json_path, 'r', encoding='utf-8') as f:
    norm_use_dict = json.load(f)

norm_default = SigilyphNormalizer({})
norm_custom = SigilyphNormalizer(norm_use_dict)

cases = [
    '您可以通过优酷APP--点击“我的”--点击头像-查看已发布的视频哦',
    '优酷APP-【我的】-【更多】-【我的客服】-【续费管理】查看是否关闭成功。',
    '2021-09-01',
    '5-3',
    '>50',
    '饱腹度>50（绿色）'
]
print('norm_use_dict', norm_use_dict)
print('default --', norm_default.before_replace_dict.get('--'))
print('custom --', norm_custom.before_replace_dict.get('--'))
for t in cases:
    print('IN:', t)
    print('OUT default:', norm_default.normalize(t, lang='zh'))
    print('OUT custom :', norm_custom.normalize(t, lang='zh'))
