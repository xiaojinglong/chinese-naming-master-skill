# -*- coding: utf-8 -*-
"""低重名取名最终报告：热名字黑名单排除 + 熟字不热字 + 命理标准不降（补水避金、五格全吉）"""
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

# 热名字黑名单（沐/泽/宇/霖/汐/轩/梓/涵/浩/然/睿/辰/宸/逸/铭…）排除后的人工甄别名单
FINAL_NAMES = ['陈沁泽', '陈泊澈', '陈泊江', '陈泊清', '陈以澄',
               '陈泊帆', '陈慕澄', '陈泊安', '陈泊佑']

final = []
for full in FINAL_NAMES:
    name = full[1:]
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        print(full, '粘连性过滤，跳过')
        continue
    if is_tacky_name(full, tacky_names):
        print(full, '俗名过滤，跳过')
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
              'requirement': '低重名取名：排除热名字（沐/泽/宇/霖/汐/轩/梓/涵等），采用"熟字不热字"策略；命理标准不降——补水抑火、避忌神金、五格全吉，双水组合优先'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_lowdup_final_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 低重名 9 强 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  "
          f"五格:{s.get('wuge_shuli')} 五行:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} "
          f"寓意:{s.get('yiyi')} 语感:{s.get('modern_sense')}")
print('\n报告:', result['report_path'])
