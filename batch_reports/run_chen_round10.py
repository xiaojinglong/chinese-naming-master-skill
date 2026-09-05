# -*- coding: utf-8 -*-
"""继续挖掘：文言句式 + 山水意象 + 水木土安全区，八字优先计分"""
import sys, os, json
BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)
from name_generator import load_hanzi_db, load_surnames, calc_wuge, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi

hanzi_map = load_hanzi_db('expanded'); surname_map = load_surnames()
scoring_data = load_data('expanded'); literature_map = load_literature_map()
bazi = get_bazi(2026, 8, 29, 20)

# 1. 查字
print('=== 用字查证 ===')
for ch in ['川','山','溪','渊','源','涧','汀','岳','野','星','青','晏','悠','然',
           '苇','航','帆','知','思','观','闻','见','亦','与','若','方','未','央','一','叙','淮']:
    info = hanzi_map.get(ch)
    print(ch, (info.get('pinyin'), info.get('wuxing'), info.get('strokes_kangxi')) if info else 'NOT IN DB')

# 2. 评分（八字优先：八字40/音韵25/寓意25/字形10，剥离五格惩罚）
def wuge_penalty_factor(r, name):
    nums = r.get('wuge_numbers') or []
    if len(nums) < 5:
        return 1.0
    tian, ren, di, wai, zong = nums
    def luck_bad(n):
        e = scoring_data['wuge']['numbers'][n - 1] if 0 < n <= len(scoring_data['wuge']['numbers']) else None
        g = str(e.get('grade', '')) if isinstance(e, dict) else ''
        return '凶' in g
    p = 1.0
    if luck_bad(ren) or luck_bad(di) or luck_bad(zong):
        p *= 0.5
    elif luck_bad(wai):
        p *= 0.85
    return p

CANDS = ['陈亦川','陈与川','陈见川','陈望川','陈闻川','陈叙川',
         '陈闻溪','陈见溪','陈亦溪','陈一苇','陈苇航','陈苇洲',
         '陈若渊','陈慕渊','陈思源','陈知源','陈望源','陈见源',
         '陈见山','陈与山','陈望岳','陈见岳','陈未央','陈晏清',
         '陈亦然','陈悠然','陈以深','陈慕深','陈闻远','陈见远']

print('\n=== 评分（八字优先计分） ===')
rows = []
for full in CANDS:
    name = full[1:]
    if any(c not in hanzi_map for c in name):
        print(full, '字不在字库:', [c for c in name if c not in hanzi_map]); continue
    w = calc_wuge('陈', name, hanzi_map, surname_map)
    if not w or not w.get('wuge_numbers'):
        print(full, 'wuge fail'); continue
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=bazi.xiyongshen, jiyongshen=bazi.jiyongshen, zodiac=bazi.zodiac,
                   wuge_numbers=w['wuge_numbers'], sancai_wuxing=w['sancai_wuxing'],
                   weight_preset='default', literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    s = r['scores']
    pen = s.get('penalty', 1.0) / max(wuge_penalty_factor(r, name), 1e-6) if s.get('penalty') else 1.0
    pen = min(max(pen, 0.3), 1.0)
    total = (s.get('wuxing_buyi', 0) * 0.40 + s.get('yinyun', 0) * 0.25 +
             s.get('yiyi', 0) * 0.25 + s.get('zixing', 0) * 0.10) * pen
    rows.append((full, round(total, 1), s.get('wuxing_buyi'), s.get('yinyun'),
                 s.get('yiyi'), s.get('wuge_shuli'),
                 hanzi_map[name[0]].get('wuxing') + '/' + hanzi_map[name[-1]].get('wuxing'),
                 w['wuge_numbers']))

rows.sort(key=lambda x: -x[1])
for full, t, wx, yy, yiyi, wg, w5, nums in rows:
    print(f'{full}  {t}  八字:{wx} 音韵:{yy} 寓意:{yiyi} 五格(参):{wg} 用字:{w5} 格:{nums}')
