# -*- coding: utf-8 -*-
"""陈姓男宝 2026-08-29 20:37 取名 —— 末字固定为拼音 qi 的字"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import generate_names, load_hanzi_db, load_surnames, calc_wuge
from scoring_engine import load_data, score_name

hanzi_map = load_hanzi_db('expanded')

# 1. 找出所有拼音 qi 的字
import unicodedata

def strip_tone(py):
    # 去声调符号：qí -> qi
    return unicodedata.normalize('NFD', py).encode('ascii', 'ignore').decode()

qi_chars = []
for ch, info in hanzi_map.items():
    pys = [p.strip() for p in str(info.get('pinyin', '')).split(',') if p.strip()]
    if any(strip_tone(p).lower() == 'qi' for p in pys):
        qi_chars.append((ch, info))
print('拼音qi的字共', len(qi_chars), '个:')
for ch, info in sorted(qi_chars, key=lambda x: x[1].get('strokes_kangxi') or 0):
    print(' ', ch, info.get('pinyin'), '五行:', info.get('wuxing'),
          '康熙笔画:', info.get('strokes_kangxi'),
          '性别:', info.get('gender_hint'), '释义:', str(info.get('meaning', ''))[:30])

# 2. 逐字生成（fixed_last_char），合并结果
merged = []
bazi_info = None
for ch, info in qi_chars:
    try:
        r = generate_names(surname='陈', gender='male',
                           birth_year=2026, birth_month=8, birth_day=29, birth_hour=20,
                           name_length=2, top_n=6, fixed_last_char=ch, diversity=False)
    except Exception as e:
        print('skip', ch, e)
        continue
    if bazi_info is None:
        bazi_info = r['bazi']
    for c in r['candidates']:
        if c['name'][-1] != ch:
            continue
        c['_qi_char'] = ch
        merged.append(c)

# 3. 去重并按总分排序
seen = {}
for c in merged:
    if c['name'] not in seen or c['total_score'] > seen[c['name']]['total_score']:
        seen[c['name']] = c
merged = sorted(seen.values(), key=lambda c: c['total_score'], reverse=True)

print('\n八字：', bazi_info['year_ganzhi'], bazi_info['month_ganzhi'],
      bazi_info['day_ganzhi'], bazi_info['hour_ganzhi'],
      '| 喜用神:', merged[0].get('xiyongshen', '') if merged else '')

print('\n=== 陈X+qi 组合排名（前 25）===')
for i, c in enumerate(merged[:25], 1):
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})")

# 保存供报告使用
out = {
    'bazi': {
        'year_ganzhi': bazi_info['year_ganzhi'], 'month_ganzhi': bazi_info['month_ganzhi'],
        'day_ganzhi': bazi_info['day_ganzhi'], 'hour_ganzhi': bazi_info['hour_ganzhi'],
        'day_master': bazi_info['day_master'], 'day_master_wuxing': bazi_info['day_master_wuxing'],
        'strength': bazi_info['strength'], 'strength_score': bazi_info['strength_score'],
        'wuxing_count': bazi_info['wuxing_count'], 'nayin': bazi_info['nayin'],
    },
    'candidates': merged[:25],
    'xiyongshen': '水', 'jiyongshen': '金', 'zodiac': bazi_info['zodiac'],
}
with open(r'D:\aicode\chinese-naming-master\batch_reports\chen_qi_merged.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print('\nsaved -> chen_qi_merged.json')
