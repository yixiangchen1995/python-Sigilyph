'''
FilePath: /python-Sigilyph/sigilyph/text_norm/tmp_test_sigilyph.py
Descripttion: 
Author: Yixiang Chen
version: 
Date: 2026-07-17 17:25:03
LastEditors: Yixiang Chen
LastEditTime: 2026-10-16 11:07:21
'''
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
    '饱腹度>50（绿色）',
    '好的，我这边先帮您核对一下。您要咨询的是这笔订单嘛，订单号是 20260915ABCD1234 ……好的。我再跟您确认一下，您在 2026年9月15日 14:30 左右，使用支付宝购买了一笔年度SVIP会员，当时支付的金额是 ¥35。前三个月是有新用户优惠，仅支付原价的25%就能享受svip的服务……好的，退款金额将会通过支付方式原路退回。……您是说那个支付宝账户是您爸爸的，现在已经不用了嘛，好的，您可以提供下银行卡号，6222-0212-3456-7890-123，是招商银行湖墅支行对嘛。好的，退款金额将在10个工作日内打到这张银行卡内。',
    '请问还有什么可以帮您，要换绑手机号码嘛，好的，需要您提供下信息来合适您的身份，请问您最近一次登录时间是什么时候呀，上个星期五，那就是2026年8月22日嘛，好的，您最近一次登录的城市是哪里呀，安徽亳州嘛，您最近一次登录的设备是什么呀，华为手机，您还记得具体的型号吗，pura x view嘛，好的，这一项不太对呢，麻烦您再回忆一下，是iPhone15promax。您的身份证号是什么呀，33010219640331001X嘛，好的任先生，账号已经给您重置成功了。如果您还有其他问题，可以随时拨打我们的热线：400-435-7544，或者访问我们的官网：www.youku.com/service。我们的服务时间是每天9:00-18:00。',
    '请问是youku下划线cs@service.com对吧，查找到您有两个账号，第一个是：【wraweurioiwaerou】，第二个是【浮光掠影6466】。',
    '免费业务可以拨打400 810 0580，会员业务请拨打400 810 3568。'
]
print('norm_use_dict', norm_use_dict)
print('default --', norm_default.before_replace_dict.get('--'))
print('custom --', norm_custom.before_replace_dict.get('--'))
for t in cases:
    print('IN:', t)
    print('OUT default:', norm_default.normalize(t, lang='zh'))
    print('OUT custom :', norm_custom.normalize(t, lang='zh'))
