# -*- coding: utf-8 -*-
"""全自由取名最终报告：96万组合穷举 + 人工甄别后的 12 强"""
import sys, os

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

FINAL_NAMES = ['陈沐泽', '陈沐汐', '陈沐江', '陈沐鸿', '陈沁泽', '陈泓宇',
               '陈沛泽', '陈泓润', '陈奕霖', '陈奕清', '陈彦霖', '陈沐言']

final = []
for full in FINAL_NAMES:
    name = full[1:]
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        continue
    if is_tacky_name(full, tacky_names):
        continue
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'],
                   sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default',
                   literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    r['surname'] = '陈'
    final.append(r)

final.sort(key=lambda x: x['total_score'], reverse=True)

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': len(final),
              'requirement': '全自由取名（不限末字）：96万组合穷举（至少一水补喜用神、避忌神金、五格预筛全吉）→ 28134 过三重门槛 → 人工甄别现代语感'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_free_final_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 全自由取名 12 强 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  "
          f"五格:{s.get('wuge_shuli')} 五行:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} "
          f"寓意:{s.get('yiyi')} 语感:{s.get('modern_sense')}")
print('\n报告:', result['report_path'])
