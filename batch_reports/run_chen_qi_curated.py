# -*- coding: utf-8 -*-
"""陈姓男宝 2026-08-29 20:37 取名 —— 末字固定为拼音 qi（精选用字）"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import generate_names, load_hanzi_db
from report_generator import generate_html_report

# 适合取名的 qi 字精选（淇=水，最契合喜用神；其余为常见佳字）
QI_CURATED = ['淇', '祺', '琦', '琪', '麒', '骐', '启', '奇', '齐', '棋', '祁', '颀', '岐', '期', '旗', '圻', '绮', '气', '起', '其']

hanzi_map = load_hanzi_db('expanded')

merged = []
bazi_info = None
for ch in QI_CURATED:
    if ch not in hanzi_map:
        continue
    try:
        r = generate_names(surname='陈', gender='male',
                           birth_year=2026, birth_month=8, birth_day=29, birth_hour=20,
                           name_length=2, top_n=8, fixed_last_char=ch, diversity=False)
    except Exception as e:
        print('skip', ch, e)
        continue
    if bazi_info is None:
        bazi_info = r['bazi']
    got = []
    for c in r['candidates']:
        if c['name'][-1] != ch:
            continue
        got.append(c)
        c['_qi_char'] = ch
        merged.append(c)
    print(f'{ch}: ' + '  '.join(f"{c['full_name']}({c['total_score']})" for c in got[:5]))

# 去重排序
seen = {}
for c in merged:
    if c['name'] not in seen or c['total_score'] > seen[c['name']]['total_score']:
        seen[c['name']] = c
merged = sorted(seen.values(), key=lambda c: c['total_score'], reverse=True)

print('\n=== 陈X+qi（精选）组合排名 前20 ===')
for i, c in enumerate(merged[:20], 1):
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})")

# 组装 result 并生成 HTML 报告
result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth_year': 2026, 'birth_month': 8, 'birth_day': 29, 'birth_hour': 20,
              'name_length': 2, 'top_n': 20, 'requirement': '末字拼音为 qi'},
    'bazi': bazi_info,
    'xiyongshen': '水', 'jiyongshen': '金', 'zodiac': bazi_info['zodiac'],
    'candidates': merged[:20],
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_qi_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)
print('\n报告:', result['report_path'])

with open(os.path.join(BASE, 'batch_reports', 'chen_qi_top.json'), 'w', encoding='utf-8') as f:
    json.dump([{'name': c['name'], 'full_name': c['full_name'], 'score': c['total_score'],
                'grade': c['grade'], 'scores': c.get('scores')} for c in merged[:20]],
               f, ensure_ascii=False, indent=1, default=str)
