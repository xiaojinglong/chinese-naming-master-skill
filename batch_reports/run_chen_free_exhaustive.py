# -*- coding: utf-8 -*-
"""陈姓男宝全自由穷举：不限末字
池：常用字（一二级）× 常用字，至少一水（喜用神），避金（忌神）
五格预筛：人格16+a / 地格a+b / 总格16+a+b 全吉，外格b+1 吉或半吉
评分硬门槛：五行补益>=85 且 五格>=70 且 音韵>=75
输出 top 300 JSON 供人工甄别
"""
import sys, os, json, time
BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

bazi = get_bazi(2026, 8, 29, 20)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac
print('喜用:', xiyong, '忌用:', jiyong, '生肖:', zodiac)

nums = scoring_data['wuge']['numbers']
LUCKY = set(); HALF = set()
for x in nums:
    g = str(x.get('grade', ''))
    n = int(x['number'])
    if '吉' in g and '凶' not in g and '半' not in g:
        LUCKY.add(n)
    elif '半吉' in g:
        HALF.add(n)

# 常用字池（水/木/中性可，排除金）
WATER, OTHER = [], []
for ch, info in hanzi_map.items():
    if ch == '陈':
        continue
    if info.get('rare_flag') or info.get('difficult_flag'):
        continue
    if info.get('tgh_level') not in (1, 2):
        continue
    if info.get('gender_hint') == 'female':
        continue
    wx = info.get('wuxing')
    if wx == '金':
        continue
    st = info.get('strokes_kangxi')
    if not st or not (2 <= st <= 24):
        continue
    if wx == '水':
        WATER.append((ch, st))
    else:
        OTHER.append((ch, st))
print(f'水字池: {len(WATER)}  其他非金字池: {len(OTHER)}')

t0 = time.time()
# 五格预筛：a 首字笔画、b 末字笔画
combos = []
by_a = {}
for a, sa in WATER + OTHER:
    by_a.setdefault(sa, []).append(a)
for a, sa in WATER + OTHER:
    renge = 16 + sa
    if renge not in LUCKY:
        continue
    for sb in by_a:
        dge = sa + sb
        zge = 16 + sa + sb
        wge = sb + 1
        if dge in LUCKY and zge in LUCKY and wge in (LUCKY | HALF):
            for b in by_a[sb]:
                if b == a:
                    continue
                wa = a in dict(WATER)
                wb = b in dict(WATER)
                if not (wa or wb):  # 至少一水
                    continue
                combos.append((a, b))
print(f'五格全吉组合（至少一水）: {len(combos)}, 预筛耗时 {time.time()-t0:.1f}s')

t0 = time.time()
water_set = dict(WATER)
results = []
for a, b in combos:
    name = a + b
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
    if s.get('wuxing_buyi', 0) >= 85 and s.get('wuge_shuli', 0) >= 70 and s.get('yinyun', 0) >= 75:
        r['_both_water'] = (a in water_set) and (b in water_set)
        results.append(r)
print(f'评分通过三重门槛: {len(results)} 个, 耗时 {time.time()-t0:.1f}s')

results.sort(key=lambda x: -x['total_score'])
print('\n=== Top 60（三重门槛全过） ===')
for i, c in enumerate(results[:60], 1):
    s = c.get('scores', {})
    tag = '双水' if c['_both_water'] else '水+X'
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}({c['grade'][:1]})  "
          f"五格:{s.get('wuge_shuli')} 五行:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} "
          f"寓意:{s.get('yiyi')} 字形:{s.get('zixing')} 语感:{s.get('modern_sense')}  {tag}")

out = [{k: c.get(k) for k in ('full_name', 'name', 'total_score', 'grade', 'scores', '_both_water')} for c in results[:300]]
with open(os.path.join(BASE, 'batch_reports', 'chen_free_exhaustive_top.json'), 'w', encoding='utf-8') as fp:
    json.dump(out, fp, ensure_ascii=False, indent=1, default=str)
print('\nsaved -> batch_reports/chen_free_exhaustive_top.json')
