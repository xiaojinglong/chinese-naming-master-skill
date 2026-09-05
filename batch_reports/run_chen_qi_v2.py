# -*- coding: utf-8 -*-
"""陈X+qi —— 以「好听优先」的人工拟定清单 + 引擎校验"""
import sys, os, json

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

# 好听优先的人工清单（首字均为现代取名常见、发音清爽的字）
CURATED = [
    # 首字声调为仄（3/4声）→ 平仄平格律，收音上扬
    '宇淇', '宇祺', '宇琦',
    '煜祺', '煜淇',
    '亦淇', '亦祺',
    '若淇', '若祺',
    '景淇', '景祺',
    '慕淇', '慕祺',
    '牧淇',
    '屹祺',
    '予淇', '予祺',
    '以淇',
    '禹淇', '禹祺',
    '奕淇', '奕祺',
    '彦淇', '彦祺',
    # 平声首字 → 柔和连读
    '沐淇', '沐祺',
    '书淇', '书祺',
    '嘉淇', '嘉祺', '嘉琦',
    '子淇', '子祺',
    '思淇', '思祺',
    '知淇', '知祺',
    '之淇',
    '泓淇', '清淇', '澄淇',
    '安淇', '安祺',
    '家淇', '家祺',
    '青淇',
]

rows = []
for name in CURATED:
    f, q = name[0], name[1]
    if f not in hanzi_map or q not in hanzi_map:
        print('缺字:', name)
        continue
    full = '陈' + name
    if not check_surname_name_stickiness('陈', name, hanzi_map):
        print('粘连/谐音过滤:', name)
        continue
    if is_tacky_name(full, tacky_names):
        print('俗气过滤:', name)
        continue
    wuge_info = calc_wuge('陈', name, hanzi_map, surname_map)
    if not wuge_info or not wuge_info.get('wuge_numbers'):
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
print('\n=== 好听清单引擎校验排名 ===')
for i, r in enumerate(rows, 1):
    print(f"{i:2d}. {r['name']}  {r['score']}分({r['grade']}) 音韵:{r['yinyun']} 五格:{r['wuge']} "
          f"寓意:{r['yiyi']} 语感:{r['modern']} 五行:{r['wuxing']} 扣分系数:{r['penalty']}")

# 生成报告
from report_generator import generate_html_report
cands = [r['result'] for r in rows[:14]]
for c in cands:
    c['surname'] = '陈'
result = {
    'input': {'surname': '陈', 'gender': 'male', 'birth': '2026-08-29 20:37',
              'name_length': 2, 'top_n': 14, 'requirement': '末字拼音 qi · 好听优先人工拟定'},
    'bazi': bazi.to_dict(),
    'xiyongshen': xiyong, 'jiyongshen': jiyong, 'zodiac': zodiac,
    'candidates': cands,
}
out = os.path.join(BASE, 'batch_reports', 'chen_qi_v2_report.html')
result['report_path'] = generate_html_report(result, output_path=out)
print('\n报告:', result['report_path'])
