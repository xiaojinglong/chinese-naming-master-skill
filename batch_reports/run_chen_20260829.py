# -*- coding: utf-8 -*-
"""陈姓男宝 2026-08-29 20:37 取名"""
import sys, os, json

BASE = r'D:\aicode\chinese-naming-master'
sys.path.insert(0, os.path.join(BASE, '_tools'))
os.chdir(BASE)

from name_generator import generate_names_with_report

result = generate_names_with_report(
    surname='陈',
    gender='male',
    birth_year=2026, birth_month=8, birth_day=29, birth_hour=20,
    name_length=2,
    top_n=12,
    style='大气',
    output_path=r'D:\aicode\chinese-naming-master\batch_reports\chen_boy_20260829_report.html'
)

bazi = result['bazi']
print('四柱：', bazi['year_ganzhi'], bazi['month_ganzhi'], bazi['day_ganzhi'], bazi['hour_ganzhi'])
print('日主：', bazi['day_master'], bazi['day_master_wuxing'], '强弱:', bazi['strength'], bazi.get('strength_score'))
print('喜用神:', result['xiyongshen'], '| 忌用神:', result.get('jiyongshen'))
print('生肖:', result['zodiac'], '| 纳音:', bazi.get('nayin'))
print('五行统计:', json.dumps(bazi.get('wuxing_count', {}), ensure_ascii=False))
print('调候:', bazi.get('tiahou', ''))

print('\n候选名：')
for i, c in enumerate(result['candidates'], 1):
    print(i, c['full_name'], c['total_score'], c['grade'])

print('\n报告:', result['report_path'])
