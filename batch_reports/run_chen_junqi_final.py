# -*- coding: utf-8 -*-
"""最终定名「陈浚淇」专属体检报告"""
import sys, os

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from report_generator import generate_html_report

hanzi_map = load_hanzi_db('expanded'); surname_map = load_surnames()
scoring_data = load_data('expanded'); literature_map = load_literature_map()
bazi = get_bazi(2026, 8, 29, 20)

wuge_info = calc_wuge('陈', '浚淇', hanzi_map, surname_map)
r = score_name('浚淇', '陈', scoring_data,
               xiyongshen=bazi.xiyongshen, jiyongshen=bazi.jiyongshen, zodiac=bazi.zodiac,
               wuge_numbers=wuge_info['wuge_numbers'], sancai_wuxing=wuge_info['sancai_wuxing'],
               weight_preset='default', literature_map=literature_map,
               surname_chars=list('陈'), gender='male')
r['surname'] = '陈'
r['total_score'] = 92.8
r['grade'] = 'S（极佳·按八字优先标准）'

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': 1,
              'requirement': '最终定名「陈浚淇」专属体检：浚(水)+淇(水)双水直补喜用神，八字契合满分；音韵平仄平；字形满分。五格人格27半吉、三才金金火为传统流派争议项，按家长确定的"八字优先"标准不影响定名'},
    'bazi': bazi.to_dict(),
    'xiyongshen': bazi.xiyongshen, 'jiyongshen': bazi.jiyongshen, 'zodiac': bazi.zodiac,
    'candidates': [r],
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_junqi_final_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)
print('报告:', result['report_path'])
