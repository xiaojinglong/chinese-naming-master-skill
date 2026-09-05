# -*- coding: utf-8 -*-
"""陈X+qi 全库穷举最优报告：43136 组合评分 → 双硬门槛 → 人工命名适格甄别 → 最终报告"""
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

# 全库穷举后人工甄别的最终名单（全部通过五行补益>=85 & 五格>=70 双硬门槛）
# 水水双补组：衍淇/泳淇/勉淇/治淇/湛淇
# 木水顺局组（备选风格）：楷淇/彦淇
FINAL_NAMES = ['陈衍淇', '陈泳淇', '陈勉淇', '陈湛淇', '陈治淇', '陈楷淇', '陈彦淇']

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
              'requirement': '全库穷举搜寻（43136 个组合逐一评分）：末字拼音 qi，五行/五格/八字全维度最优'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_qi_exhaustive_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 全库穷举最终推荐 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  五格:{s.get('wuge_shuli')} 五行:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')}")
print('\n报告:', result['report_path'])
