# -*- coding: utf-8 -*-
"""赵姓女宝（2026-08-30 出生）取名：喜木忌水 + 现代偏好模型 + 八字优先计分"""
import sys, os

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import load_hanzi_db, load_surnames, calc_wuge, check_surname_name_stickiness, is_tacky_name, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi
from report_generator import generate_html_report
from modern_taste import modern_score

hanzi_map = load_hanzi_db('expanded')
surname_map = load_surnames()
scoring_data = load_data('expanded')
literature_map = load_literature_map()
tacky_names = scoring_data.get('tacky_names', set())

# 时辰未知：除午时外各时辰喜用神稳定为喜木忌水，按主流取 h=10
bazi = get_bazi(2026, 8, 30, 10)
xiyong, jiyong, zodiac = bazi.xiyongshen, bazi.jiyongshen, bazi.zodiac
print('八字:', bazi.to_dict().get('year_ganzhi'), bazi.to_dict().get('month_ganzhi'),
      bazi.to_dict().get('day_ganzhi'), bazi.to_dict().get('hour_ganzhi'),
      '| 日主:', bazi.to_dict().get('day_master'), bazi.to_dict().get('strength'),
      '| 喜:', xiyong, '忌:', jiyong, '| 五行:', bazi.to_dict().get('wuxing_count'))

# 候选：引擎候选 + 现代偏好模型手工组（动态词/虚词起 + 品质字收，木属性为主）
# 已人工排除谐音雷：赵可宜≈可疑、赵以棠≈已糖、赵柔柔类
FINAL_NAMES = [
    # 引擎原生候选
    '赵若谷', '赵书瑶', '赵书宁', '赵今棠', '赵萱朵',
    # 模型定制：木木双补 / 木+虚词
    '赵奕棠', '赵若宜', '赵可槿', '赵予乔', '赵其蓁',
    '赵以芊', '赵亦柠', '赵唯棠', '赵若乔', '赵宥棠',
]

final = []
wuge_of = {}
for full in FINAL_NAMES:
    name = full[1:]
    if any(c not in hanzi_map for c in name):
        print(full, '字不在字库，跳过'); continue
    if is_tacky_name(full, tacky_names):
        print(full, '俗名过滤，跳过'); continue
    wuge_info = calc_wuge('赵', name, hanzi_map, surname_map)
    if not wuge_info or not wuge_info.get('wuge_numbers'):
        print(full, '五格计算失败，跳过'); continue
    r = score_name(name, '赵', scoring_data,
                   xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'],
                   sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default',
                   literature_map=literature_map,
                   surname_chars=list('赵'), gender='female')
    r['surname'] = '赵'
    r['full_name'] = full
    final.append(r)
    wuge_of[full] = wuge_info['wuge_numbers']

# ===== 八字优先计分（与陈家一致的口径）：八字40% + 音韵25% + 寓意25% + 字形10% =====
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
    full = r['full_name']
    penalty = s.get('penalty', 1.0)
    wp = wuge_penalty_factor(wuge_of.get(full), r['name'])
    adj_penalty = penalty / wp if wp > 0 else penalty
    total = (s.get('wuxing_buyi', 0) * BAZI_W['wuxing'] +
             s.get('yinyun', 0) * BAZI_W['yinyun'] +
             s.get('yiyi', 0) * BAZI_W['yiyi'] +
             s.get('zixing', 0) * BAZI_W['zixing']) * adj_penalty
    # 融入现代偏好模型分（好听/气质维度）
    ms_dict = modern_score('赵', r['name'], hanzi_map)
    ms = ms_dict.get('total', 50) if isinstance(ms_dict, dict) else ms_dict
    r['modern_taste'] = ms
    r['modern_taste_detail'] = ms_dict if isinstance(ms_dict, dict) else {}
    total = total * 0.8 + ms * 0.2
    r['total_score'] = round(total, 1)
    r['grade'] = get_grade(total)

final.sort(key=lambda x: (x['total_score'], x['scores'].get('wuge_shuli', 0)), reverse=True)

result = {
    'input': {'surname': '赵', 'gender': 'female',
              'birth': '2026-08-30（时辰未知，按喜用神稳定的非午时口径排盘）',
              'name_length': 2, 'top_n': len(final),
              'requirement': '女宝取名：八字喜木忌水（原局木为0，补木为第一刚需）；以现代偏好模型把关听感（动态词起、品质字收、清亮声母、熟字冷用）；八字优先计分，五格仅参考'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': final,
}
out_path = os.path.join(BASE, 'batch_reports', 'zhao_girl_20260830_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('\n=== 赵姓女宝 定稿 ===')
for i, c in enumerate(final, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分 ({c['grade']})  "
          f"八字:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} 寓意:{s.get('yiyi')} "
          f"字形:{s.get('zixing')} 偏好:{c['modern_taste']} 五格(参):{s.get('wuge_shuli')}")
print('\n报告:', result['report_path'])
