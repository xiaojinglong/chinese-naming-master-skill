# -*- coding: utf-8 -*-
"""现代偏好模型驱动的取名：动态词 × 平声抽象收尾，八字约束不降"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from modern_taste import modern_score, get_tone

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())
bazi = get_bazi(2026, 8, 29, 20)

# P1 动态词（中字，需仄声）× 抽象/状态收尾字（末字，需平声）
DYNAMIC_MID = ['浚', '望', '慕', '牧', '见', '奕', '既', '以', '宥', '允',
               '亦', '与', '宇', '雨', '若', '可']
ABSTRACT_END = ['淇', '明', '白', '清', '和', '淮', '安', '南', '然', '之', '宁']

rows = []
for mid in DYNAMIC_MID:
    for end in ABSTRACT_END:
        name = mid + end
        if any(c not in hanzi_map for c in name):
            continue
        wx = [hanzi_map[c].get('wuxing') for c in name]
        if '金' in wx:                      # 忌神
            continue
        if '火' in wx:                      # 火旺避火
            continue
        if wx.count('水') < 1:              # 至少一水补喜用神
            continue
        # 声调结构：中字仄声 + 末字平声（模型黄金构型）
        t_mid, t_end = get_tone(hanzi_map, mid), get_tone(hanzi_map, end)
        if t_mid not in (3, 4) or t_end not in (1, 2):
            continue
        full = '陈' + name
        if not check_surname_name_stickiness('陈', name, hanzi_map):
            continue
        if is_tacky_name(full, tacky_names):
            continue
        wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
        if not wuge_info or not wuge_info.get('wuge_numbers'):
            continue
        r = score_name(name, '陈', scoring_data,
                       xiyongshen=bazi.xiyongshen, jiyongshen=bazi.jiyongshen, zodiac=bazi.zodiac,
                       wuge_numbers=wuge_info['wuge_numbers'], sancai_wuxing=wuge_info['sancai_wuxing'],
                       weight_preset='default', literature_map=literature_map,
                       surname_chars=list('陈'), gender='male')
        s = r['scores']
        # 引擎门槛：音韵+寓意不过线的一票否决
        if s.get('yinyun', 0) < 75 or s.get('yiyi', 0) < 85:
            continue
        ms = modern_score('陈', name, hanzi_map)
        composite = ms['total'] * 0.60 + s.get('yinyun', 0) * 0.25 + s.get('yiyi', 0) * 0.15
        rows.append({'full': full, 'name': name, 'ms': ms, 'r': r,
                     'composite': round(composite, 1),
                     'yinyun': s.get('yinyun'), 'yiyi': s.get('yiyi'),
                     'wuxing_buyi': s.get('wuxing_buyi'),
                     'wuge': s.get('wuge_shuli'), 'wuge_nums': wuge_info['wuge_numbers'],
                     'wx': '/'.join(wx)})

rows.sort(key=lambda x: -x['composite'])
print(f'共 {len(rows)} 个组合过约束+门槛，Top 15：')
for i, x in enumerate(rows[:15], 1):
    print(f"{i:2d}. {x['full']}  综合:{x['composite']}  现代偏好:{x['ms']['total']}"
          f"(气质:{x['ms']['temperament']} 声调:{x['ms']['tone_structure']} 声母:{x['ms']['brightness']})"
          f"  音韵:{x['yinyun']} 寓意:{x['yiyi']} 五行:{x['wuxing_buyi']} 用字:{x['wx']}")

with open(os.path.join(BASE, 'batch_reports', 'chen_modern_taste_top.json'), 'w', encoding='utf-8') as f:
    json.dump(rows[:15], f, ensure_ascii=False, default=str)
print('\n已保存 chen_modern_taste_top.json')
