# -*- coding: utf-8 -*-
"""八字优先报告：五行补益+生肖契合为唯一硬标准，五格仅作参考展示"""
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

# 大候选池：现代顺口的 双水 / 水+木 组合（八字喜水、水生木帮扶乙木）
CANDS = [
    # 双水
    '陈沐泽','陈润泽','陈泽霖','陈沐霖','陈清源','陈泓宇','陈泽洋','陈沐洋',
    '陈涵泽','陈浩泽','陈浩霖','陈浩源','陈瀚霖','陈瀚泽','陈润霖','陈润宇',
    '陈泓霖','陈泓润','陈泓涵','陈泓泽','陈沛泽','陈沁泽','陈慕泽','陈牧泽',
    '陈泓清','陈沐清','陈清和','陈润和','陈泽清','陈沐涵','陈泽润','陈泽泓',
    '陈沛霖','陈涵霖','陈沁霖','陈清霖','陈泓洲','陈泽源','陈沐洲','陈泽澜',
    # 水+木 / 木+水
    '陈泽楷','陈楷泽','陈泽彦','陈彦泽','陈奕泽','陈泽奕','陈嘉泽','陈景泽',
    '陈泽嘉','陈泽林','陈林泽','陈柏泽','陈松泽','陈泽松','陈桐泽','陈泽森',
    '陈泽荣','陈泽贤','陈泽谦','陈泽彬','陈泽杰','陈泓奕','陈泓彦','陈泓嘉',
    '陈泓景','陈泓林','陈泓柏','陈泓贤','陈泓彬','陈泓杰','陈奕霖','陈奕涵',
    '陈彦霖','陈彦涵','陈嘉霖','陈景霖','陈楷霖','陈林霖','陈柏霖','陈奕淳',
]

rows = []
for full in CANDS:
    name = full[1:]
    if any(c not in hanzi_map for c in name):
        print(full, '字不在字库，跳过'); continue
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        print(full, '粘连性过滤，跳过'); continue
    if is_tacky_name(full, tacky_names):
        print(full, '俗名过滤，跳过'); continue
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    if not wuge_info or not wuge_info.get('wuge_numbers'):
        print(full, '五格计算失败，跳过'); continue
    r = score_name(name, '陈', scoring_data,
                   xiyongshen=xiyong, jiyongshen=jiyong, zodiac=zodiac,
                   wuge_numbers=wuge_info['wuge_numbers'],
                   sancai_wuxing=wuge_info['sancai_wuxing'],
                   weight_preset='default',
                   literature_map=literature_map,
                   surname_chars=list('陈'), gender='male')
    s = r.get('scores', {})
    rows.append({
        'r': r, 'full': full,
        'wuge_numbers': wuge_info['wuge_numbers'],
        'bazi_fit': s.get('wuxing_buyi', 0),   # 八字契合 = 五行补益（含生肖）
        'yinyun': s.get('yinyun', 0),
        'wuge': s.get('wuge_shuli', 0),
    })

# ===== 八字优先模式：重算总分 =====
# 引擎原权重中五格占 18%，且乘法惩罚含五格凶数硬砍（核心三格凶×0.5）。
# 本模式将五格权重与数理惩罚全部摘除（五格仅展示参考），
# 八字契合（五行补益+生肖）提为 35%，其余维度重新分配。
BAZI_W = {'wuxing': 0.35, 'yinyun': 0.20, 'yiyi': 0.20, 'modern': 0.15, 'zixing': 0.10, 'wuge': 0.0}

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

for x in rows:
    r = x['r']; s = r['scores']
    penalty = s.get('penalty', 1.0)
    wp = wuge_penalty_factor(x['wuge_numbers'], r['name'])
    adj_penalty = penalty / wp if wp > 0 else penalty  # 剥离数理惩罚，保留谐音/俗气/老气惩罚
    total = (s.get('wuxing_buyi', 0) * BAZI_W['wuxing'] +
             s.get('yinyun', 0) * BAZI_W['yinyun'] +
             s.get('yiyi', 0) * BAZI_W['yiyi'] +
             s.get('modern_sense', 0) * BAZI_W['modern'] +
             s.get('zixing', 0) * BAZI_W['zixing']) * adj_penalty
    x['bazi_total'] = round(total, 1)
    x['bazi_grade'] = get_grade(total)
    x['adj_penalty'] = round(adj_penalty, 2)

# 八字契合度为唯一录取标准：先过 90 分线，再按 八字优先总分 排序
passed = [x for x in rows if x['bazi_fit'] >= 90]
passed.sort(key=lambda x: (-x['bazi_fit'], -x['bazi_total']))
print(f'\n候选池 {len(rows)} 个，八字契合≥90 的 {len(passed)} 个（按 八字>八字优先总分 排序）：')
for i, x in enumerate(passed, 1):
    s = x['r'].get('scores', {})
    print(f"{i:2d}. {x['full']}  八字:{x['bazi_fit']}  八字优先总分:{x['bazi_total']}({x['bazi_grade'][0]})  "
          f"音韵:{x['yinyun']}  寓意:{s.get('yiyi')}  语感:{s.get('modern_sense')}  五格:{x['wuge']}(参考)")

# 取前 12 名生成报告（八字契合优先；五格仅参考不参与排序）
TOP = []
for x in passed[:12]:
    r = x['r']
    r['total_score'] = x['bazi_total']
    r['grade'] = x['bazi_grade']
    r['surname'] = '陈'
    TOP.append(r)

result = {
    'input': {'surname': '陈', 'gender': 'male',
              'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': len(TOP),
              'requirement': '八字优先取名：以八字契合度（五行补益+生肖喜忌，喜水忌金）为唯一录取标准，双水/水木组合优先；五格数理仅作参考、不设门槛；用字以现代顺口为前提'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': TOP,
}
out_path = os.path.join(BASE, 'batch_reports', 'chen_bazi_first_report.html')
result['report_path'] = generate_html_report(result, output_path=out_path)

print('\n=== 八字优先 12 强（五格仅参考、不参与评分） ===')
for i, c in enumerate(TOP, 1):
    s = c.get('scores', {})
    print(f"{i:2d}. {c['full_name']}  {c['total_score']}分({c['grade']})  "
          f"八字:{s.get('wuxing_buyi')} 音韵:{s.get('yinyun')} 五格(参考):{s.get('wuge_shuli')} 寓意:{s.get('yiyi')}")
print('\n报告:', result['report_path'])
