# -*- coding: utf-8 -*-
"""最终报告：好听优先 + 五行不犯忌 + 五格全吉 策略的四强"""
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

FINAL_NAMES = ['陈奕淇', '陈楷淇', '陈宥淇', '陈彦淇']

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
              'requirement': '好听优先 + 五行不犯忌（忌金）+ 五格全吉 + 末字拼音 qi（淇）'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_final_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 最终四强 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  五格:{s.get('wuge_shuli')} 音韵:{s.get('yinyun')} 五行:{s.get('wuxing_buyi')}")
print('\n报告:', result['report_path'])
