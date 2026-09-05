# -*- coding: utf-8 -*-
"""现代偏好模型定稿报告：Top 10 候选（模型生成 + 人工谐音甄别）"""
import sys, os, json

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

data = json.load(open(os.path.join(BASE, 'batch_reports', 'chen_modern_taste_top.json'), encoding='utf-8'))

# 人工谐音复查后的定稿（101 过线组合中取 Top10，无谐音雷）
FINAL = ['陈宥清', '陈雨淇', '陈以清', '陈允清', '陈雨清',
         '陈以和', '陈允和', '陈雨白', '陈可清', '陈奕清']

final = []
wuge_of = {}
for full in FINAL:
    name = full[1:]
    rec = next((x for x in data if x['full'] == full), None)
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=bazi.xiyongshen, jiyongshen=bazi.jiyongshen, zodiac=bazi.zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'], sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default', literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    r['surname'] = '陈'
    r['total_score'] = rec['composite']
    r['grade'] = 'S（极佳）' if rec['composite'] >= 90 else 'A（优秀）'
    final.append(r)
    wuge_of[full] = wuge_info['wuge_numbers']

final.sort(key=lambda x: x['total_score'], reverse=True)

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': len(final),
              'requirement': '现代偏好模型驱动取名（_tools/modern_taste.py）：以最终定名「陈浚淇」收获的一手好评数据 + 11 轮好恶反馈提炼四条规律——P1 动态词>静态名词且末字收在品质上、P2 j/q/x/y 清亮声母、P3 仄起平收（4-2 黄金声调）、P4 熟字冷用。八字约束不降：至少一水补喜用神、避忌神金、火旺避火；引擎音韵≥75 寓意≥85 门槛'},
    'bazi': bazi.to_dict(),
    'xiyongshen': bazi.xiyongshen, 'jiyongshen': bazi.jiyongshen, 'zodiac': bazi.zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_modern_taste_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)
print('=== 现代偏好模型定稿 Top10 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}({c['grade'][:1]})  "
          f"音韵:{s.get('yinyun')} 寓意:{s.get('yiyi')} 五行:{s.get('wuxing_buyi')}")
print('\n报告:', result['report_path'])
