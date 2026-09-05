# -*- coding: utf-8 -*-
"""陈X+qi 定制组合评分：手工扩充首字池，逐一评分对比"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from name_generator import load_literature_map

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

bazi = get_bazi(2026, 8, 29, 20)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac

# 首字池：水属性为主（喜用神），兼少量中性大气字
FIRST_CHARS = ['泓', '沛', '泽', '浩', '涵', '沐', '澄', '润', '清', '源',
               '宇', '嘉', '书', '子', '文', '景', '煜', '晋', '俊', '若',
               '思', '永', '之', '以', '云', '雨', '浚', '湛', '涣', '汲',
               '润', '瀚', '洋', '汇', '治', '泰', '海', '波', '晖', '明',
               '弘', '宏', '洲', '恒', '沧', '和', '平', '林', '松', '柏']
# 末字池：适合男孩取名的 qi 字
QI_CHARS = ['淇', '祺', '琦', '琪', '麒', '骐', '启', '奇', '齐', '棋', '祁', '颀', '岐', '期', '旗', '圻']

results = []
for f in FIRST_CHARS:
    if f not in hanzi_map:
        continue
    for q in QI_CHARS:
        if q not in hanzi_map:
            continue
        name = f + q
        full = '陈' + name
        # 基本过滤
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
        r['_qi'] = q
        results.append(r)

results.sort(key=lambda x: x['total_score'], reverse=True)

print('总组合数:', len(results))
print('\n=== Top 30 陈X+qi ===')
for i, c in enumerate(results[:30], 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分({c['grade']}) "
          f"五格:{s.get('wuge_shuli')} 音韵:{s.get('yinyun')} 寓意:{s.get('yiyi')} "
          f"语感:{s.get('modern_sense')} 五行:{s.get('wuxing_buyi')} 系数:{s.get('penalty')}")

# 每个 qi 字的最佳首字
print('\n=== 各 qi 字最佳组合 ===')
best = {}
for c in results:
    q = c['_qi']
    if q not in best:
        best[q] = c
for q, c in sorted(best.items(), key=lambda kv: kv[1]['total_score'], reverse=True):
    print(f"  {q} -> {c['full_name']} {c['total_score']}分")

with open(os.path.join(BASE, 'batch_reports', 'chen_qi_manual_top.json'), 'w', encoding='utf-8') as fp:
    json.dump([{k: c.get(k) for k in ('full_name', 'name', 'total_score', 'grade', 'scores')} for c in results[:30]],
              fp, ensure_ascii=False, indent=1, default=str)
