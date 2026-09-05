# -*- coding: utf-8 -*-
"""陈X+qi 全库穷举：五行/五格/八字各方面最优搜寻
首字池：通用规范一级汉字、非生僻、非难认、性别适配男孩、五行属水或木（八字喜用）
末字池：16 个适合取名的 qi 字
硬门槛：五行补益>=85 且 五格数理>=70，再按总分排名，输出 Top 名单与 JSON
"""
import sys, os, json, time
BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from name_generator import load_literature_map

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

bazi = get_bazi(2026, 8, 29, 20)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac
print('喜用神:', xiyong, '忌用神:', jiyong, '生肖:', zodiac)

QI_CHARS = ['淇', '祺', '琦', '琪', '麒', '骐', '启', '奇', '齐', '棋', '祁', '颀', '岐', '期', '旗', '圻']

# 首字池：一级常用字 + 非生僻非难认 + 男孩适配 + 水木属性
first_chars = []
for ch, info in hanzi_map.items():
    if ch in QI_CHARS or ch == '陈':
        continue
    if info.get('rare_flag') or info.get('difficult_flag'):
        continue
    if info.get('tgh_level') not in (1, 2):  # 一二级常用
        continue
    if info.get('gender_hint') == 'female':
        continue
    if info.get('wuxing') not in ('水', '木'):
        continue
    first_chars.append(ch)
print('首字池大小:', len(first_chars), '× qi字:', len(QI_CHARS), '=', len(first_chars)*len(QI_CHARS))

t0 = time.time()
results = []
fails = 0
for f in first_chars:
    finfo = hanzi_map[f]
    # 首字多音字或拼音异常的跳过太苛刻，保留；homophone_risk 首字先不硬卡，最后人工复查
    for q in QI_CHARS:
        name = f + q
        full = '陈' + name
        if not check_surname_name_stickiness('陈', name, hanzi_map):
            continue
        if is_tacky_name(full, tacky_names):
            continue
        wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
        if not wuge_info or not wuge_info.get('wuge_numbers'):
            continue
        r = score_name(name, '陈', scoring_data,
                       xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                       wuge_numbers=wuge_info['wuge_numbers'],
                       sancai_wuxing=wuge_info['sancai_wuxing'],
                       weight_preset='default',
                       literature_map=literature_map,
                       surname_chars=list('陈'), gender='male')
        s = r.get('scores', {})
        r['_qi'] = q
        r['_first_wuxing'] = finfo.get('wuxing')
        results.append(r)

print(f'评分完成: {len(results)} 个组合, 耗时 {time.time()-t0:.1f}s')

# 硬门槛：五行补益>=85 且 五格>=70
elite = [r for r in results if (r.get('scores', {}).get('wuxing_buyi', 0) >= 85
                                 and r.get('scores', {}).get('wuge_shuli', 0) >= 70)]
print('过双门槛（五行>=85 & 五格>=70）:', len(elite))

elite.sort(key=lambda x: (-x['total_score'], -x['scores'].get('yinyun', 0)))

print('\n=== 全库穷举 Top 25（已过硬门槛） ===')
for i, c in enumerate(elite[:25], 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}({c['grade']})  "
          f"五格:{s.get('wuge_shuli')} 五行:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} "
          f"寓意:{s.get('yiyi')} 语感:{s.get('modern_sense')}  首字五行:{c['_first_wuxing']} 三才:{c.get('sancai_wuxing')}")

# 各 qi 字的最优代表
print('\n=== 各 qi 字最佳组合 ===')
best = {}
for c in elite:
    q = c['_qi']
    if q not in best:
        best[q] = c
for q, c in sorted(best.items(), key=lambda kv: -kv[1]['total_score']):
    s = c['scores']
    print(f"  {q} -> {c['full_name']} {c['total_score']} (五格{s.get('wuge_shuli')} 五行{s.get('wuxing_buyi')} 音韵{s.get('yinyun')})")

out = [{k: c.get(k) for k in ('full_name', 'name', 'total_score', 'grade', 'scores', '_qi', '_first_wuxing')} for c in elite[:40]]
with open(os.path.join(BASE, 'batch_reports', 'chen_qi_exhaustive_top.json'), 'w', encoding='utf-8') as fp:
    json.dump(out, fp, ensure_ascii=False, indent=1, default=str)
print('\nsaved -> batch_reports/chen_qi_exhaustive_top.json')
