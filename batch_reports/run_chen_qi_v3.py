# -*- coding: utf-8 -*-
"""陈X+qi v3：好听 × 五格吉数 双重筛选
原理：陈=康熙16画。配末字(淇12画)时，首字康熙笔画 5/9/13/17/23 可使人格/地格/总格全吉；
配末字(祺/琦/琪13画)时，首字 8/18 画全吉。"""
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

# 按五格吉数笔画 + 发音顺口人工拟定
CURATED = [
    # 末字=淇(12画)，首字9画：泰/泉/昱/波/治/泊
    '泰淇', '泉淇', '昱淇',
    # 末字=淇，首字5画：永/世/玉/正
    '永淇', '世淇', '玉淇',
    # 末字=淇，首字13画：焕/靖/湘/敬/雷/楠
    '焕淇', '靖淇', '湘淇', '敬淇', '楠淇',
    # 末字=淇，首字17画：泽/鸿/璟
    '泽淇', '鸿淇', '璟淇',
    # 末字=祺(13画)，首字8画：沐/沛/昊/明/松/青/佳/宗/昕/坤
    '沐祺', '沛祺', '昊祺', '明祺', '松祺', '青祺', '佳祺', '宗祺', '昕祺', '坤祺',
    # 末字=祺，首字18画：涛/谦/济/滨
    '涛祺', '谦祺', '济祺', '滨祺',
    # 末字=琦/琪(13画)，首字8画：沐/沛/昊/佳
    '沐琦', '沛琦', '昊琦', '佳琪', '昊琪', '沛琪',
    # 末字=骐/麒(18画) 检查：地格=a+18, 需试算，先放入让引擎判定
    '泽骐', '煜骐', '昊骐', '泽麒',
]

rows = []
skipped = []
for name in CURATED:
    if name[0] not in hanzi_map or name[1] not in hanzi_map:
        skipped.append((name, '缺字'))
        continue
    full = '陈' + name
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        skipped.append((name, '谐音/粘连'))
        continue
    if is_tacky_name(full, tacky_names):
        skipped.append((name, '俗气'))
        continue
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    if not wuge_info or not wuge_info.get('wuge_numbers'):
        skipped.append((name, '五格缺数据'))
        continue
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'],
                   sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default', literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    s = r.get('scores', {})
    rows.append({'name': full, 'score': r['total_score'], 'grade': r['grade'],
                 'yinyun': s.get('yinyun'), 'wuge': s.get('wuge_shuli'),
                 'yiyi': s.get('yiyi'), 'modern': s.get('modern_sense'),
                 'wuxing': s.get('wuxing_buyi'), 'penalty': s.get('penalty'),
                 'result': r})

rows.sort(key=lambda x: x['score'], reverse=True)
if skipped:
    print('过滤:', skipped)
print('\n=== 好听×五格吉数 排名 ===')
for i, r in enumerate(rows, 1):
    print(f"{i:2d}. {r['name']}  {r['score']}分({r['grade']}) 音韵:{r['yinyun']} 五格:{r['wuge']} "
          f"寓意:{r['yiyi']} 语感:{r['modern']} 五行:{r['wuxing']} 系数:{r['penalty']}")

# 报告
cands = [r['result'] for r in rows[:12]]
for c in cands:
    c['surname'] = '陈'
result = {
    'input': {'surname': '陈', 'gender': 'male', 'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': 12,
              'requirement': '末字拼音 qi · 好听优先 + 五格吉数笔画筛选'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': cands,
}
out = os.path.join(BASE, 'batch_reports', 'chen_qi_v3_report.html')
result['report_path'] = generate_html_report(result, output_path=out)
print('\n报告:', result['report_path'])
