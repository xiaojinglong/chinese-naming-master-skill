# -*- coding: utf-8 -*-
"""陈X+qi 最终报告生成"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from report_generator import generate_html_report

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

bazi = get_bazi(2026, 8, 29, 20)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac

FIRST_CHARS = ['泓', '沛', '泽', '浩', '涵', '沐', '澄', '润', '清', '源',
               '宇', '嘉', '书', '子', '文', '景', '煜', '晋', '俊', '若',
               '思', '永', '之', '以', '云', '雨', '浚', '湛', '瀚', '洋',
               '汇', '治', '泰', '海', '波', '晖', '明', '弘', '宏', '洲',
               '恒', '沧', '和', '平', '林', '松', '柏', '彦', '宗', '志']
QI_CHARS = ['淇', '祺', '琦', '琪', '麒', '骐', '启', '奇', '齐', '棋', '祁', '颀', '岐', '期', '旗', '圻']

results = {}
for f in FIRST_CHARS:
    if f not in hanzi_map:
        continue
    for q in QI_CHARS:
        if q not in hanzi_map:
            continue
        name = f + q
        full = '陈' + name
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
        results[name] = r

all_ranked = sorted(results.values(), key=lambda x: x['total_score'], reverse=True)

# 取名策略：Top12 全局 + 每个 qi 字的最佳代表，去重取前 16
final = []
seen = set()
for c in all_ranked:
    if c['name'] in seen:
        continue
    final.append(c)
    seen.add(c['name'])
    if len(final) >= 12:
        break
best_per_qi = {}
for c in all_ranked:
    q = c['_qi']
    if q not in best_per_qi and q in ('淇', '祺', '琦', '琪', '骐', '麒', '启', '齐', '棋', '期'):
        best_per_qi[q] = c
for q, c in sorted(best_per_qi.items(), key=lambda kv: kv[1]['total_score'], reverse=True):
    if c['name'] not in seen:
        final.append(c)
        seen.add(c['name'])

final = sorted(final, key=lambda x: x['total_score'], reverse=True)[:16]
for c in final:
    c['surname'] = '陈'

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': 16,
              'requirement': '末字拼音为 qi（淇/祺/琦/琪/骐/麒/启/齐/棋/期等）'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_qi_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 最终推荐（陈X+qi）===')
for i, c in enumerate(final, 1):
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})")
print('\n报告:', result['report_path'])
