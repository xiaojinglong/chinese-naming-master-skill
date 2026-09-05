# -*- coding: utf-8 -*-
"""破晓·既明系定稿报告：文言"既X"句式 + 光明意象 + 八字优先计分（五格仅参考）"""
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

# 破晓/既明系：双水组（望明/向明/沐白）+ 既字系（既明/既和/既清/既白/见明）
# 注：破晓意象中的火属性字（晓/曦/昕/旦/昭/晞）全部排除——宝宝火已过旺；
#     「明」在姓名学中属水，是光明意象里唯一的水属性字，恰好可用。
FINAL_NAMES = ['陈望明', '陈向明', '陈沐白', '陈既明', '陈既和',
               '陈既清', '陈既白', '陈见明']

final = []
wuge_of = {}
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
    wuge_of[full] = wuge_info['wuge_numbers']

# ===== 八字优先计分：八字40% + 音韵25% + 寓意25% + 字形10% =====
BAZI_W = {'wuxing': 0.40, 'yinyun': 0.25, 'yiyi': 0.25, 'zixing': 0.10}

def get_grade(score):
    if score >= 90: return 'S（极佳）'
    if score >= 80: return 'A（优秀）'
    if score >= 70: return 'B（良好）'
    if score >= 60: return 'C（合格）'
    if score >= 50: return 'D（一般）'
    return 'F（不推荐）'

def wuge_penalty_factor(wuge_numbers, name):
    """复现引擎的五格数理乘法惩罚（用于剥离）"""
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

for r in final:
    s = r['scores']
    penalty = s.get('penalty', 1.0)
    wp = wuge_penalty_factor(wuge_of.get(r['surname'] + r['name'], r.get('wuge_numbers')), r['name'])
    adj_penalty = penalty / wp if wp > 0 else penalty
    total = (s.get('wuxing_buyi', 0) * BAZI_W['wuxing'] +
             s.get('yinyun', 0) * BAZI_W['yinyun'] +
             s.get('yiyi', 0) * BAZI_W['yiyi'] +
             s.get('zixing', 0) * BAZI_W['zixing']) * adj_penalty
    r['total_score'] = round(total, 1)
    r['grade'] = get_grade(total)

final.sort(key=lambda x: (x['total_score'], x['scores'].get('wuge_shuli', 0)), reverse=True)

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': len(final),
              'requirement': '破晓·既明系取名：沿用用户认可的「陈既明」方向（文言"既X"句式 + 光明意象）。破晓系火属性字（晓/曦/昕/旦/昭）因八字火旺全部排除，「明」属水为光明意象唯一可用核心字；双水组（望明/向明/沐白）八字契合满分，既字系（既明/既白/既和/既清）水生木帮身；五格仅作参考不设门槛；重名率极低'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_jiming_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('=== 破晓·既明系定稿（八字优先计分） ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  "
          f"八字:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} "
          f"寓意:{s.get('yiyi')} 五格(参考):{s.get('wuge_shuli')}")
print('\n报告:', result['report_path'])
