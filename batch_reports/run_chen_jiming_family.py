# -*- coding: utf-8 -*-
"""既明族全变体挖掘：既X / 明X / X明 三种句式 × 水木土安全区，八字优先计分"""
import sys, os

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

bazi = get_bazi(2026, 8, 29, 20)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac

SAFE = ['清','安','泽','平','嘉','和','澈','淮','洲','可','若','雨','沐',
        '宇','永','宥','亦','以','允','远','旭','见','与','向','望','白']

CANDS = []
for ch in SAFE:                     # 既X
    CANDS.append('既' + ch)
for ch in SAFE:                     # 明X
    CANDS.append('明' + ch)
for ch in SAFE:                     # X明
    CANDS.append(ch + '明')

rows = []
for name in CANDS:
    full = '陈' + name
    if any(c not in hanzi_map for c in name):
        continue
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        continue
    if is_tacky_name(full, tacky_names):
        continue
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    if not wuge_info or not wuge_info.get('wuge_numbers'):
        continue
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'],
                   sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default',
                   literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    s = r['scores']
    rows.append({'full': full, 'name': name, 'scores': s,
                 'wuge_nums': wuge_info['wuge_numbers'],
                 'wx0': hanzi_map[name[0]].get('wuxing'),
                 'wx1': hanzi_map[name[1]].get('wuxing') if len(name) > 1 else ''})

# ===== 八字优先计分：八字40% + 音韵25% + 寓意25% + 字形10%（五格剥离） =====
BAZI_W = {'wuxing': 0.40, 'yinyun': 0.25, 'yiyi': 0.25, 'zixing': 0.10}

def get_grade(score):
    if score >= 90: return 'S'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'

def wuge_penalty_factor(wuge_numbers, name):
    if not wuge_numbers:
        return 1.0
    XIONG = (2, 4, 9, 10, 12, 14, 19, 20, 22, 28, 34, 36, 40, 42, 43, 44,
             46, 49, 54, 56, 59, 60, 62, 64, 66, 69, 70, 72, 74, 76, 79, 80)
    BANXIONG = (26, 27, 30, 50, 53, 55)
    f = 1.0
    core_idx = (1, 2, 4)
    core_xiong = any(i < len(wuge_numbers) and wuge_numbers[i] in XIONG for i in core_idx)
    wai_xiong = len(wuge_numbers) > 3 and wuge_numbers[3] in XIONG
    core_banxiong = any(i < len(wuge_numbers) and wuge_numbers[i] in BANXIONG for i in core_idx)
    if core_xiong:
        f *= 0.5
    elif core_banxiong:
        f *= 0.9
    if wai_xiong and len(name) > 1:
        f *= 0.85
    return f

for x in rows:
    s = x['scores']
    penalty = s.get('penalty', 1.0)
    wp = wuge_penalty_factor(x['wuge_nums'], x['name'])
    adj = penalty / wp if wp > 0 else penalty
    total = (s.get('wuxing_buyi', 0) * BAZI_W['wuxing'] +
             s.get('yinyun', 0) * BAZI_W['yinyun'] +
             s.get('yiyi', 0) * BAZI_W['yiyi'] +
             s.get('zixing', 0) * BAZI_W['zixing']) * adj
    x['total'] = round(total, 1)
    x['grade'] = get_grade(total)

rows.sort(key=lambda x: (x['total'], x['scores'].get('wuge_shuli', 0)), reverse=True)

print(f'共测 {len(rows)} 个既明族变体，Top 30：')
for i, x in enumerate(rows[:30], 1):
    s = x['scores']
    print(f"{i:2d}. {x['full']}  {x['total']}({x['grade']})  "
          f"八字:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} 寓意:{s.get('yiyi')} "
          f"五格(参):{s.get('wuge_shuli')}  用字:{x['wx0']}+{x['wx1']}  格:{x['wuge_nums']}")

# 保存全部结果供报告用
import json
with open(os.path.join(BASE, 'batch_reports', 'chen_jiming_family_all.json'), 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, default=str)
print('\n已保存全量结果到 chen_jiming_family_all.json')
